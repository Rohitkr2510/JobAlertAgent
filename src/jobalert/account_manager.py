import hashlib
import json
import os
from datetime import UTC, datetime
from pathlib import Path
from urllib.parse import urlparse

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow

from jobalert.database import Database
from jobalert.gmail_client import SCOPES
from jobalert.token_store import TokenVault


def _configure_local_oauth_transport() -> None:
    redirect_uri = os.getenv("JOBALERT_REDIRECT_URI", "http://localhost:8501")
    parsed = urlparse(redirect_uri)
    if parsed.scheme == "http" and parsed.hostname == "localhost":
        os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"


_configure_local_oauth_transport()


class AccountManager:
    def __init__(self, database: Database, vault: TokenVault):
        self.database = database
        self.vault = vault

    def authorization_url(
        self,
        credentials_path: Path,
        redirect_uri: str,
        email_hint: str,
    ) -> tuple[str, str, str]:
        flow = Flow.from_client_secrets_file(
            credentials_path,
            scopes=SCOPES,
        )
        flow.redirect_uri = redirect_uri

        url, state = flow.authorization_url(
            access_type="offline",
            include_granted_scopes="true",
            prompt="consent select_account",
            login_hint=email_hint,
        )

        return url, state, flow.code_verifier

    def complete_authorization(
        self,
        credentials_path: Path,
        redirect_uri: str,
        authorization_response: str,
        state: str,
        code_verifier: str | None = None,
    ) -> str:
        from googleapiclient.discovery import build

        flow = Flow.from_client_secrets_file(credentials_path, scopes=SCOPES, state=state)
        flow.redirect_uri = redirect_uri
        flow.fetch_token(
            authorization_response=authorization_response,
            code_verifier=code_verifier,
        )
        service = build("gmail", "v1", credentials=flow.credentials, cache_discovery=False)
        email = service.users().getProfile(userId="me").execute()["emailAddress"]
        self.upsert(email, flow.credentials)
        return email

    def upsert(self, email: str, credentials: Credentials) -> None:
        account_id = hashlib.sha256(email.lower().encode()).hexdigest()[:20]
        encrypted = self.vault.encrypt(credentials.to_json())
        with self.database.connect() as connection:
            connection.execute(
                """INSERT INTO accounts
                (account_id, email, token_encrypted, enabled, created_at)
                VALUES (?, ?, ?, 1, ?)
                ON CONFLICT(email) DO UPDATE SET
                token_encrypted=excluded.token_encrypted, enabled=1, last_error=NULL""",
                (account_id, email, encrypted, datetime.now(UTC).isoformat()),
            )

    def credentials(self, email: str) -> Credentials:
        with self.database.connect() as connection:
            row = connection.execute("SELECT token_encrypted FROM accounts WHERE email = ? AND enabled = 1", (email,)).fetchone()
        if not row:
            raise KeyError(f"Enabled account not found: {email}")
        info = json.loads(self.vault.decrypt(row["token_encrypted"]))
        credentials = Credentials.from_authorized_user_info(info, SCOPES)
        if credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
            self.upsert(email, credentials)
        return credentials

    def set_enabled(self, email: str, enabled: bool) -> None:
        with self.database.connect() as connection:
            connection.execute("UPDATE accounts SET enabled = ? WHERE email = ?", (int(enabled), email))

    def remove(self, email: str) -> None:
        with self.database.connect() as connection:
            connection.execute("DELETE FROM accounts WHERE email = ?", (email,))
