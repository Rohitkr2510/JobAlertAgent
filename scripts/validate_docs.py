"""Validate repository documentation and extract Mermaid diagrams for rendering."""

import argparse
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = {
    "README.md",
    "SECURITY.md",
    "CONTRIBUTING.md",
    "CODE_OF_CONDUCT.md",
    "SUPPORT.md",
    "CHANGELOG.md",
    "docs/index.md",
    "docs/architecture/system-architecture.md",
    "docs/operations/runbook.md",
    "docs/security/threat-model.md",
    "docs/releases/release-checklist.md",
}
LINK = re.compile(r"(?<!!)\[[^]]+\]\(([^)]+)\)")
MERMAID = re.compile(r"```mermaid\s*\n(.*?)```", re.DOTALL)
PERSONAL_EMAIL = re.compile(r"(?i)\b(?![^@\s]+@example\.com\b)[\w.+-]+@gmail\.com\b")


def markdown_files() -> list[Path]:
    return sorted(path for path in ROOT.rglob("*.md") if not {".git", ".venv", "htmlcov"}.intersection(path.parts))


def validate() -> list[tuple[Path, str]]:
    errors: list[tuple[Path, str]] = []
    for relative in sorted(REQUIRED):
        if not (ROOT / relative).is_file():
            errors.append((ROOT / relative, "required file is missing"))
    for path in markdown_files():
        text = path.read_text(encoding="utf-8")
        if PERSONAL_EMAIL.search(text):
            errors.append((path, "personal Gmail address is forbidden"))
        headings = [line for line in text.splitlines() if line.startswith("# ")]
        if ".github" not in path.parts and len(headings) != 1:
            errors.append((path, f"expected one H1 heading, found {len(headings)}"))
        if text.count("```mermaid") != len(MERMAID.findall(text)):
            errors.append((path, "unclosed Mermaid code fence"))
        for target in LINK.findall(text):
            if target.startswith(("http://", "https://", "mailto:", "#")):
                continue
            clean = target.split("#", 1)[0]
            if clean and not (path.parent / clean).resolve().exists():
                errors.append((path, f"broken local link: {target}"))
    return errors


def extract_mermaid(destination: Path) -> int:
    destination.mkdir(parents=True, exist_ok=True)
    count = 0
    for path in markdown_files():
        for diagram in MERMAID.findall(path.read_text(encoding="utf-8")):
            count += 1
            (destination / f"diagram-{count:02d}.mmd").write_text(diagram, encoding="utf-8")
    return count


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--extract-mermaid", type=Path)
    args = parser.parse_args()
    errors = validate()
    if errors:
        for path, message in errors:
            print(f"{path.relative_to(ROOT)}: {message}")
        raise SystemExit(1)
    count = extract_mermaid(args.extract_mermaid) if args.extract_mermaid else 0
    print(f"documentation validation: pass ({len(markdown_files())} files, {count} diagrams)")


if __name__ == "__main__":
    main()
