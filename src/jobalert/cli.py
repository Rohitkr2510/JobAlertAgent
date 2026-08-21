import argparse
from pathlib import Path

from jobalert.config import load_config
from jobalert.database import save_new
from jobalert.gmail_client import authenticate, fetch_messages
from jobalert.parser import parse_eml, parse_message
from jobalert.report import write_report
from jobalert.scoring import is_recent, score_job
from jobalert.selfcheck import run_self_check


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(prog="jobalert")
    commands = root.add_subparsers(dest="command", required=True)
    commands.add_parser("self-check")
    auth = commands.add_parser("gmail-auth")
    auth.add_argument("--credentials", type=Path, required=True)
    auth.add_argument("--token", type=Path, required=True)
    for name in ("collect-eml", "collect-gmail"):
        command = commands.add_parser(name)
        if name == "collect-eml":
            command.add_argument("maildir", type=Path)
        else:
            command.add_argument("--credentials", type=Path, required=True)
            command.add_argument("--token", type=Path, required=True)
        command.add_argument("--config", type=Path, default=Path("config/job-filters.yaml"))
        command.add_argument("--output", type=Path, default=Path("reports"))
        command.add_argument("--database", type=Path, default=Path("data/jobs.db"))
    return root


def main() -> None:
    args = parser().parse_args()
    if args.command == "self-check":
        for name, status in run_self_check().items():
            print(f"{name}: {status}")
        return
    if args.command == "gmail-auth":
        authenticate(args.credentials, args.token)
        print("Gmail authorization saved.")
        return
    config = load_config(args.config)
    jobs = []
    if args.command == "collect-eml":
        for path in args.maildir.glob("*.eml"):
            jobs.extend(parse_eml(path))
    else:
        for message in fetch_messages(args.credentials, args.token, config.hours, config.sender_domains):
            jobs.extend(parse_message(message))
    jobs = [job for job in jobs if is_recent(job, config)]
    jobs = save_new([score_job(job, config) for job in jobs], args.database)
    report = write_report(jobs, args.output)
    print(f"New jobs: {len(jobs)}")
    print(f"Report: {report}")


if __name__ == "__main__":
    main()
