import base64
from email import policy
from email.parser import BytesParser
from pathlib import Path

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]


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
    sender_query = " OR ".join(f"from:({domain})" for domain in domains)
    query = f"newer_than:{max(1, (hours + 23) // 24)}d ({sender_query})"
    response = service.users().messages().list(userId="me", q=query, maxResults=500).execute()
    for item in response.get("messages", []):
        raw = (
            service.users()
            .messages()
            .get(userId="me", id=item["id"], format="raw")
            .execute()["raw"]
        )
        yield BytesParser(policy=policy.default).parsebytes(base64.urlsafe_b64decode(raw + "=="))
