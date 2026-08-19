import re
from collections.abc import Iterable
from pathlib import Path

from releaseguard.models import Finding, Severity, display_path
from releaseguard.policy import Policy

IGNORED_PARTS = {".git", ".venv", "node_modules", "__pycache__", "reports"}
SECRET_PATTERNS = {
    "AWS access key": re.compile(r"AKIA[0-9A-Z]{16}"),
    "Private key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    "Generic credential": re.compile(
        r"(?i)(?:password|passwd|api[_-]?key|secret)\s*[:=]\s*['\"][^'\"\s]{8,}['\"]"
    ),
}


def iter_files(root: Path) -> Iterable[Path]:
    for item in root.rglob("*"):
        if item.is_file() and not any(part in IGNORED_PARTS for part in item.parts):
            yield item


def check_required_files(root: Path, policy: Policy) -> list[Finding]:
    findings = []
    for name in policy.required_files:
        if not (root / name).is_file():
            findings.append(
                Finding(
                    check="required_files",
                    severity=Severity.BLOCKER,
                    message=f"Required release file is missing: {name}",
                    path=name,
                    remediation=f"Add {name} before promotion.",
                )
            )
    return findings


def check_dockerfile(root: Path, policy: Policy) -> list[Finding]:
    dockerfile = root / "Dockerfile"
    if not dockerfile.is_file():
        return []
    text = dockerfile.read_text(encoding="utf-8", errors="ignore")
    findings = []
    if policy.docker.require_non_root_user and not re.search(r"(?mi)^USER\s+(?!root\s*$).+", text):
        findings.append(
            Finding(
                check="docker",
                severity=Severity.BLOCKER,
                message="Dockerfile does not select a non-root runtime user.",
                path="Dockerfile",
                remediation="Create an unprivileged user and add a USER instruction.",
            )
        )
    if policy.docker.require_healthcheck and not re.search(r"(?mi)^HEALTHCHECK\s+", text):
        findings.append(
            Finding(
                check="docker",
                severity=Severity.WARNING,
                message="Dockerfile has no HEALTHCHECK instruction.",
                path="Dockerfile",
                remediation="Add a health check for the primary service endpoint.",
            )
        )
    if policy.docker.prohibit_latest_tag and re.search(r"(?mi)^FROM\s+\S+:latest(?:\s|$)", text):
        findings.append(
            Finding(
                check="docker",
                severity=Severity.WARNING,
                message="Docker base image uses the mutable latest tag.",
                path="Dockerfile",
                remediation="Pin a major/minor version or immutable digest.",
            )
        )
    return findings


def check_large_files(root: Path, policy: Policy) -> list[Finding]:
    limit = policy.repository.prohibit_large_files_mb * 1024 * 1024
    findings = []
    for path in iter_files(root):
        if path.stat().st_size > limit:
            findings.append(
                Finding(
                    check="repository",
                    severity=Severity.WARNING,
                    message=f"File exceeds {policy.repository.prohibit_large_files_mb} MB.",
                    path=display_path(path, root),
                    remediation="Move large artifacts to an artifact registry.",
                )
            )
    return findings


def check_secrets(root: Path, policy: Policy) -> list[Finding]:
    if not policy.repository.scan_secrets:
        return []
    findings = []
    for path in iter_files(root):
        if path.stat().st_size > 1_000_000:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        for label, pattern in SECRET_PATTERNS.items():
            if pattern.search(text):
                findings.append(
                    Finding(
                        check="secrets",
                        severity=Severity.BLOCKER,
                        message=f"Potential {label.lower()} detected.",
                        path=display_path(path, root),
                        remediation="Remove and rotate the credential; use a secret store.",
                    )
                )
    return findings

