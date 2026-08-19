from dataclasses import dataclass, field
from datetime import datetime


@dataclass(slots=True)
class Job:
    title: str
    company: str
    location: str
    url: str
    source: str
    email_received_at: datetime
    experience: str = "Not mentioned"
    text: str = ""
    posted_at: datetime | None = None
    date_verified: bool = False
    skills: list[str] = field(default_factory=list)
    score: int = 0
    priority: str = "Needs Review"
    reason: str = ""
    account_email: str = "Local import"
    application_status: str = "New"

    @property
    def unique_id(self) -> str:
        import hashlib

        raw = f"{self.source}|{self.url or self.title.lower()}|{self.company.lower()}"
        return hashlib.sha256(raw.encode()).hexdigest()[:20]
