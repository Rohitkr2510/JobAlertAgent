from pathlib import Path

from releaseguard.engine import scan
from releaseguard.models import Status
from releaseguard.policy import Policy

GOOD_DOCKERFILE = """FROM python:3.12-slim
RUN useradd -m app
USER app
HEALTHCHECK CMD python -c 'print(1)'
"""


def create_release_files(root: Path) -> None:
    for name in ("README.md", "CHANGELOG.md", "rollback.md"):
        (root / name).write_text(f"# {name}\n", encoding="utf-8")
    (root / "Dockerfile").write_text(GOOD_DOCKERFILE, encoding="utf-8")


def test_clean_repository_passes(tmp_path: Path) -> None:
    create_release_files(tmp_path)
    result = scan(tmp_path, Policy(required_files=["README.md", "Dockerfile"]))
    assert result.status == Status.PASS
    assert result.score == 100


def test_missing_file_blocks_release(tmp_path: Path) -> None:
    result = scan(tmp_path, Policy(required_files=["rollback.md"]))
    assert result.status == Status.BLOCKED
    assert result.score == 70


def test_secret_blocks_release(tmp_path: Path) -> None:
    create_release_files(tmp_path)
    credential = "api" + '_key = "123456789-secret"'
    (tmp_path / "settings.py").write_text(credential, encoding="utf-8")
    result = scan(tmp_path, Policy())
    assert result.status == Status.BLOCKED
    assert any(item.check == "secrets" for item in result.findings)
