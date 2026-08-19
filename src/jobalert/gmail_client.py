import base64
from collections.abc import Iterator
from email import policy
from email.parser import BytesParser
from pathlib import Path
from typing import Any

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]


def build_query(hours: int, domains: list[str]) -> str:
    """Build a Gmail search that safely narrows the server-side result set."""
    days = max(1, (hours + 23) // 24)
    senders = " OR ".join(f"from:({domain})" for domain in domains)
    return f"newer_than:{days}d ({senders})"


def iter_message_ids(service: Any, query: str) -> Iterator[str]:
    """Yield every matching message ID across Gmail result pages."""
    page_token = None
    while True:
        response = (
            service.users()
            .messages()
            .list(userId="me", q=query, maxResults=500, pageToken=page_token)
            .execute()
        )
        yield from (item["id"] for item in response.get("messages", []))
        page_token = response.get("nextPageToken")
        if not page_token:
            return


def decode_raw_message(raw: str):
    padding = "=" * (-len(raw) % 4)
    payload = base64.urlsafe_b64decode(raw + padding)
    return BytesParser(policy=policy.default).parsebytes(payload)


def _credentials(credentials_path: Path, token_path: Path):
    try:
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
    except ImportError as error:
        raise RuntimeError("Install Gmail support with: pip install -e '.[gmail]'") from error
    credentials = (
        Credentials.from_authorized_user_file(token_path, SCOPES) if token_path.exists() else None
    )
    if credentials and credentials.expired and credentials.refresh_token:
        credentials.refresh(Request())
    if not credentials or not credentials.valid:
        credentials = InstalledAppFlow.from_client_secrets_file(
            credentials_path, SCOPES
        ).run_local_server(port=0)
    token_path.parent.mkdir(parents=True, exist_ok=True)
    token_path.write_text(credentials.to_json(), encoding="utf-8")
    return credentials


def authenticate(credentials_path: Path, token_path: Path) -> None:
    _credentials(credentials_path, token_path)


def fetch_messages(credentials_path: Path, token_path: Path, hours: int, domains: list[str]):
    from googleapiclient.discovery import build

    service = build("gmail", "v1", credentials=_credentials(credentials_path, token_path))
    for message_id in iter_message_ids(service, build_query(hours, domains)):
        response = (
            service.users().messages().get(userId="me", id=message_id, format="raw").execute()
        )
        yield decode_raw_message(response["raw"])
