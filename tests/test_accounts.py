from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest
from google.oauth2.credentials import Credentials

from jobalert.account_manager import AccountManager
from jobalert.database import Database
from jobalert.gmail_client import SCOPES
from jobalert.token_store import TokenVault


def test_account_tokens_are_encrypted_and_removable(tmp_path: Path) -> None:
    database = Database(tmp_path / "jobs.db")
    manager = AccountManager(database, TokenVault(tmp_path / "token.key"))
    credentials = Credentials(
        token="access-token",
        refresh_token="refresh-token",
        token_uri="https://oauth2.googleapis.com/token",
        client_id="client-id",
        client_secret="client-secret",
        scopes=SCOPES,
        expiry=datetime.now(UTC) + timedelta(hours=1),
    )
    manager.upsert("owner@example.com", credentials)
    account = database.rows("accounts")[0]
    assert account["email"] == "owner@example.com"
    assert b"access-token" not in account["token_encrypted"]
    assert manager.credentials("owner@example.com").token == "access-token"
    manager.set_enabled("owner@example.com", False)
    with pytest.raises(KeyError):
        manager.credentials("owner@example.com")
    manager.remove("owner@example.com")
    assert database.rows("accounts") == []
