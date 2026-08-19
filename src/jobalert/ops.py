import os
import sqlite3
from pathlib import Path

from fastapi import FastAPI, Response, status
from prometheus_client import CONTENT_TYPE_LATEST, CollectorRegistry, Gauge, generate_latest

from jobalert import __version__
from jobalert.config import load_config
from jobalert.database import Database
from jobalert.logging import configure_logging
from jobalert.token_store import TokenVault

ROOT = Path(os.getenv("JOBALERT_ROOT", "."))
DB_PATH = ROOT / os.getenv("JOBALERT_DATABASE", "data/jobs.db")
CONFIG_PATH = ROOT / os.getenv("JOBALERT_CONFIG", "config/job-filters.yaml")
KEY_PATH = ROOT / os.getenv("JOBALERT_TOKEN_KEY", "secrets/token.key")
REPORTS_PATH = ROOT / "reports"

configure_logging()
app = FastAPI(title="JobAlertAgent Operations", version=__version__)


@app.get("/health/live")
def liveness() -> dict[str, str]:
    return {"status": "alive", "version": __version__}


@app.get("/health/ready")
def readiness(response: Response) -> dict[str, object]:
    checks: dict[str, bool] = {}
    try:
        Database(DB_PATH)
        checks["database"] = True
    except (OSError, sqlite3.Error):
        checks["database"] = False
    try:
        load_config(CONFIG_PATH)
        checks["configuration"] = True
    except (OSError, ValueError):
        checks["configuration"] = False
    try:
        TokenVault(KEY_PATH)
        checks["token_key"] = True
    except (OSError, ValueError):
        checks["token_key"] = False
    try:
        REPORTS_PATH.mkdir(parents=True, exist_ok=True)
        probe = REPORTS_PATH / ".write-probe"
        probe.write_text("ok", encoding="utf-8")
        probe.unlink()
        checks["reports_writable"] = True
    except OSError:
        checks["reports_writable"] = False
    ready = all(checks.values())
    if not ready:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    return {"status": "ready" if ready else "not_ready", "checks": checks}


@app.get("/metrics")
def metrics() -> Response:
    database = Database(DB_PATH)
    registry = CollectorRegistry()
    connected = Gauge("jobalert_connected_accounts", "Configured Gmail accounts", registry=registry)
    enabled = Gauge("jobalert_enabled_accounts", "Enabled Gmail accounts", registry=registry)
    collected = Gauge("jobalert_jobs_collected", "Jobs stored locally", registry=registry)
    high = Gauge("jobalert_high_priority_jobs", "High-priority jobs", registry=registry)
    failed = Gauge("jobalert_sync_failures_total", "Failed synchronization runs", registry=registry)
    accounts = database.rows("accounts")
    jobs = database.rows("jobs", 100000)
    runs = database.rows("runs", 100000)
    connected.set(len(accounts))
    enabled.set(sum(bool(account["enabled"]) for account in accounts))
    collected.set(len(jobs))
    high.set(sum(job["priority"] == "High Priority" for job in jobs))
    failed.set(sum(run["status"] == "failed" for run in runs))
    return Response(generate_latest(registry), media_type=CONTENT_TYPE_LATEST)
