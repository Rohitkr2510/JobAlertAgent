from pathlib import Path

from fastapi.testclient import TestClient

from jobalert import ops


def test_operations_health_and_metrics(tmp_path: Path, monkeypatch) -> None:
    config = tmp_path / "job-filters.yaml"
    config.write_text(
        """hours: 24
minimum_score: 60
high_priority_score: 80
maximum_experience_years: 5
preferred_locations: [remote]
role_keywords: [devops]
skill_keywords: [docker]
sender_domains: [linkedin.com]
""",
        encoding="utf-8",
    )
    monkeypatch.setattr(ops, "DB_PATH", tmp_path / "jobs.db")
    monkeypatch.setattr(ops, "CONFIG_PATH", config)
    monkeypatch.setattr(ops, "KEY_PATH", tmp_path / "token.key")
    monkeypatch.setattr(ops, "REPORTS_PATH", tmp_path / "reports")
    client = TestClient(ops.app)
    assert client.get("/health/live").status_code == 200
    ready = client.get("/health/ready")
    assert ready.status_code == 200
    assert ready.json()["status"] == "ready"
    metrics = client.get("/metrics")
    assert metrics.status_code == 200
    assert "jobalert_connected_accounts" in metrics.text


def test_readiness_reports_unavailable_dependencies(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(ops, "DB_PATH", tmp_path / "missing" / "jobs.db")
    monkeypatch.setattr(ops, "CONFIG_PATH", tmp_path / "missing.yaml")
    monkeypatch.setattr(ops, "KEY_PATH", tmp_path / "missing" / "token.key")
    monkeypatch.setattr(ops, "REPORTS_PATH", Path("/proc/jobalert-reports"))

    response = TestClient(ops.app).get("/health/ready")

    assert response.status_code == 503
    assert response.json()["status"] == "not_ready"
    assert not all(response.json()["checks"].values())
