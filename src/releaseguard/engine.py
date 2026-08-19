from pathlib import Path

from releaseguard.checks import (
    check_dockerfile,
    check_large_files,
    check_required_files,
    check_secrets,
)
from releaseguard.models import ScanResult, Severity, Status
from releaseguard.policy import Policy


def scan(target: Path, policy: Policy) -> ScanResult:
    target = target.resolve()
    if not target.is_dir():
        raise NotADirectoryError(f"Scan target is not a directory: {target}")

    groups = {
        "required_files": check_required_files(target, policy),
        "docker": check_dockerfile(target, policy),
        "secrets": check_secrets(target, policy),
        "repository": check_large_files(target, policy),
    }
    findings = [finding for items in groups.values() for finding in items]
    weight_map = policy.weights.model_dump()
    score = 100
    for group, items in groups.items():
        if items:
            blocker = any(item.severity == Severity.BLOCKER for item in items)
            score -= weight_map[group] if blocker else max(1, weight_map[group] // 2)
    score = max(0, score)

    has_blocker = any(item.severity == Severity.BLOCKER for item in findings)
    if (policy.fail_on_blocker and has_blocker) or score < policy.minimum_score:
        status = Status.BLOCKED
    elif findings:
        status = Status.WARNING
    else:
        status = Status.PASS

    return ScanResult(
        target=str(target),
        status=status,
        score=score,
        findings=findings,
        checks_run=len(groups),
        policy_version=policy.version,
    )

