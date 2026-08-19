from enum import StrEnum
from pathlib import Path

from pydantic import BaseModel, Field


class Severity(StrEnum):
    INFO = "info"
    WARNING = "warning"
    BLOCKER = "blocker"


class Status(StrEnum):
    PASS = "pass"
    WARNING = "warning"
    BLOCKED = "blocked"


class Finding(BaseModel):
    check: str
    severity: Severity
    message: str
    path: str | None = None
    remediation: str | None = None


class ScanResult(BaseModel):
    target: str
    status: Status
    score: int = Field(ge=0, le=100)
    findings: list[Finding]
    checks_run: int
    policy_version: int

    @property
    def blockers(self) -> int:
        return sum(item.severity == Severity.BLOCKER for item in self.findings)


class ScanRequest(BaseModel):
    path: str = "/workspace"
    policy: str = "/app/release-policy.yaml"


def display_path(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)

