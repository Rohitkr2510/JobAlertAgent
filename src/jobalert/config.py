from dataclasses import dataclass
from pathlib import Path

import yaml


@dataclass(slots=True)
class Config:
    hours: int
    minimum_score: int
    high_priority_score: int
    maximum_experience_years: int
    preferred_locations: list[str]
    role_keywords: list[str]
    skill_keywords: list[str]
    sender_domains: list[str]


def load_config(path: Path) -> Config:
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    return Config(**raw)
