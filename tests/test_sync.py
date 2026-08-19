from datetime import UTC, datetime
from email.message import EmailMessage
from pathlib import Path
from typing import cast

import pytest

from jobalert import sync
from jobalert.account_manager import AccountManager
from jobalert.config import Config
from jobalert.database import Database
from jobalert.selfcheck import run_self_check


class FakeManager:
    def credentials(self, email: str) -> object:
        return object()


def job_message() -> EmailMessage:
    message = EmailMessage()
    message["From"] = "jobs@linkedin.com"
    message["Date"] = datetime.now(UTC).strftime("%a, %d %b %Y %H:%M:%S %z")
    message.set_content("Job alert")
    message.add_alternative(
        '<a href="https://example.com/jobs/42" data-company="Acme" '
        'data-location="Remote">DevOps Engineer</a><p>AWS Docker, 2 years</p>',
        subtype="html",
    )
    return message


def test_sync_success_and_self_check(tmp_path: Path, monkeypatch) -> None:
    database = Database(tmp_path / "jobs.db")
    config = Config(24, 60, 80, 5, ["remote"], ["devops"], ["aws", "docker"], ["linkedin.com"])
    monkeypatch.setattr(sync, "fetch_messages_with_credentials", lambda *_: [job_message()])

    result = sync.sync_account(
        "owner@example.com", cast(AccountManager, FakeManager()), database, config
    )

    assert result["emails"] == 1
    assert result["new"] == 1
    assert database.rows("runs")[0]["status"] == "success"
    assert set(run_self_check().values()) == {"pass"}


def test_sync_failure_is_recorded(tmp_path: Path, monkeypatch) -> None:
    database = Database(tmp_path / "jobs.db")
    config = Config(24, 60, 80, 5, [], [], [], [])

    def fail(*_args):
        raise RuntimeError("temporary Gmail failure")

    monkeypatch.setattr(sync, "fetch_messages_with_credentials", fail)
    with pytest.raises(RuntimeError, match="temporary Gmail failure"):
        sync.sync_account(
            "owner@example.com", cast(AccountManager, FakeManager()), database, config
        )
    assert database.rows("runs")[0]["status"] == "failed"
