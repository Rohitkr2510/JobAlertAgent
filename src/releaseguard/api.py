from pathlib import Path

from fastapi import FastAPI, HTTPException

from releaseguard import __version__
from releaseguard.engine import scan
from releaseguard.models import ScanRequest, ScanResult
from releaseguard.policy import load_policy

app = FastAPI(title="ReleaseGuard", version=__version__)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "version": __version__}


@app.post("/v1/scan", response_model=ScanResult)
def run_scan(request: ScanRequest) -> ScanResult:
    try:
        return scan(Path(request.path), load_policy(Path(request.policy)))
    except (FileNotFoundError, NotADirectoryError, ValueError) as error:
        raise HTTPException(status_code=400, detail=str(error)) from error

