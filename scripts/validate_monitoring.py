"""Validate monitoring configuration files without starting the stack."""

import json
from pathlib import Path

import yaml


def main() -> None:
    for path in Path("monitoring").rglob("*.yml"):
        yaml.safe_load(path.read_text(encoding="utf-8"))
    dashboard = Path("monitoring/grafana/dashboards/jobalert.json")
    json.loads(dashboard.read_text(encoding="utf-8"))
    print("monitoring configuration: pass")


if __name__ == "__main__":
    main()
