from datetime import UTC, datetime
from pathlib import Path

import pytest

from jobalert.database import Database
from jobalert.models import Job


def job() -> Job:
    return Job(
        "DevOps Engineer",
        "Acme",
        "Remote",
        "https://example.com/1",
        "LinkedIn",
        datetime.now(UTC),
        score=90,
        priority="High Priority",
        account_email="alerts@example.com",
    )


def test_database_deduplicates_and_tracks_status(tmp_path: Path) -> None:
    database = Database(tmp_path / "jobs.db")
    item = job()
    assert database.save_jobs([item]) == [item]
    assert database.save_jobs([item]) == []
    database.update_job_status(item.unique_id, "Applied")
    assert database.rows("jobs")[0]["application_status"] == "Applied"


def test_database_rejects_invalid_status(tmp_path: Path) -> None:
    database = Database(tmp_path / "jobs.db")
    with pytest.raises(ValueError):
        database.update_job_status("missing", "Unknown")
    with pytest.raises(ValueError, match="Unsupported table"):
        database.rows("secrets")
    assert database.setting("schedule_enabled", "false") == "false"
    database.set_setting("schedule_enabled", "true")
    assert database.setting("schedule_enabled") == "true"
