import argparse
import sys
from pathlib import Path

import uvicorn

from releaseguard.engine import scan
from releaseguard.models import Status
from releaseguard.policy import load_policy
from releaseguard.reporting import write_reports


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="releaseguard", description="Offline release gate")
    subparsers = parser.add_subparsers(dest="command", required=True)
    scan_parser = subparsers.add_parser("scan", help="Scan a repository")
    scan_parser.add_argument("target", type=Path)
    scan_parser.add_argument("--policy", type=Path, default=Path("release-policy.yaml"))
    scan_parser.add_argument("--output", type=Path, default=Path("reports"))
    serve_parser = subparsers.add_parser("serve", help="Start the REST API")
    serve_parser.add_argument("--host", default="127.0.0.1")
    serve_parser.add_argument("--port", type=int, default=8080)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    if args.command == "serve":
        uvicorn.run("releaseguard.api:app", host=args.host, port=args.port)
        return
    try:
        result = scan(args.target, load_policy(args.policy))
        json_path, html_path = write_reports(result, args.output)
    except (FileNotFoundError, NotADirectoryError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        raise SystemExit(3) from error
    print(f"Release status: {result.status.upper()}")
    print(f"Readiness score: {result.score}/100")
    print(f"Findings: {len(result.findings)}")
    print(f"JSON report: {json_path}")
    print(f"HTML report: {html_path}")
    exit_codes = {Status.PASS: 0, Status.WARNING: 1, Status.BLOCKED: 2}
    raise SystemExit(exit_codes[result.status])


if __name__ == "__main__":
    main()

