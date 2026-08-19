from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field


class DockerPolicy(BaseModel):
    require_non_root_user: bool = True
    require_healthcheck: bool = True
    prohibit_latest_tag: bool = True


class RepositoryPolicy(BaseModel):
    prohibit_large_files_mb: int = Field(default=10, ge=1)
    scan_secrets: bool = True


class Weights(BaseModel):
    required_files: int = 30
    docker: int = 40
    secrets: int = 20
    repository: int = 10


class Policy(BaseModel):
    version: int = 1
    minimum_score: int = Field(default=80, ge=0, le=100)
    fail_on_blocker: bool = True
    required_files: list[str] = []
    docker: DockerPolicy = DockerPolicy()
    repository: RepositoryPolicy = RepositoryPolicy()
    weights: Weights = Weights()


def load_policy(path: Path) -> Policy:
    if not path.is_file():
        raise FileNotFoundError(f"Policy not found: {path}")
    raw: dict[str, Any] = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return Policy.model_validate(raw)

