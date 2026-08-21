from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest
from google.oauth2.credentials import Credentials

from jobalert import account_manager
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


def test_authorization_url_returns_pkce_verifier(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    class FakeFlow:
        code_verifier = "test-code-verifier"
        redirect_uri = None

        @classmethod
        def from_client_secrets_file(cls, path: Path, scopes: list[str]) -> "FakeFlow":
            return cls()

        def authorization_url(self, **kwargs: str) -> tuple[str, str]:
            return "https://accounts.google.com/auth", "test-state"

    monkeypatch.setattr(account_manager, "Flow", FakeFlow)
    manager = AccountManager(Database(tmp_path / "jobs.db"), TokenVault(tmp_path / "token.key"))

    url, state, verifier = manager.authorization_url(
        tmp_path / "web_credentials.json",
        "http://localhost:8501",
        "owner@example.com",
    )

    assert url == "https://accounts.google.com/auth"
    assert state == "test-state"
    assert verifier == "test-code-verifier"


def test_complete_authorization_passes_pkce_verifier(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    captured: dict[str, str | None] = {}

    class FakeCredentials:
        pass

    class FakeFlow:
        redirect_uri = None
        credentials = FakeCredentials()

        @classmethod
        def from_client_secrets_file(cls, path: Path, scopes: list[str], state: str) -> "FakeFlow":
            assert state == "test-state"
            return cls()

        def fetch_token(self, **kwargs: str | None) -> None:
            captured["authorization_response"] = kwargs["authorization_response"]
            captured["code_verifier"] = kwargs["code_verifier"]

    class FakeProfile:
        def execute(self) -> dict[str, str]:
            return {"emailAddress": "owner@example.com"}

    class FakeUsers:
        def getProfile(self, userId: str) -> FakeProfile:
            return FakeProfile()

    class FakeService:
        def users(self) -> FakeUsers:
            return FakeUsers()

    def fake_build(*args: object, **kwargs: object) -> FakeService:
        return FakeService()

    monkeypatch.setattr(account_manager, "Flow", FakeFlow)
    monkeypatch.setattr("googleapiclient.discovery.build", fake_build)

    manager = AccountManager(Database(tmp_path / "jobs.db"), TokenVault(tmp_path / "token.key"))
    monkeypatch.setattr(manager, "upsert", lambda email, credentials: None)

    email = manager.complete_authorization(
        tmp_path / "web_credentials.json",
        "http://localhost:8501",
        "http://localhost:8501?code=test-code&state=test-state",
        "test-state",
        "test-code-verifier",
    )

    assert email == "owner@example.com"
    assert captured == {
        "authorization_response": "http://localhost:8501?code=test-code&state=test-state",
        "code_verifier": "test-code-verifier",
    }
