from datetime import UTC, datetime
from email.message import EmailMessage
from pathlib import Path
from tempfile import TemporaryDirectory

from jobalert.config import Config
from jobalert.database import Database
from jobalert.parser import parse_message
from jobalert.report import write_report
from jobalert.scoring import score_job
from jobalert.token_store import TokenVault


def run_self_check() -> dict[str, str]:
    with TemporaryDirectory() as directory:
        root = Path(directory)
        message = EmailMessage()
        message["From"] = "jobs@linkedin.com"
        message["Date"] = datetime.now(UTC).strftime("%a, %d %b %Y %H:%M:%S %z")
        message.set_content("Job alert")
        message.add_alternative(
            '<a href="https://example.com/jobs/1" data-company="Acme" '
            'data-location="Remote">DevOps Engineer</a>'
            "<p>AWS Docker Terraform, 2-4 years, 2 hours ago</p>",
            subtype="html",
        )
        config = Config(
            24,
            60,
            80,
            5,
            ["remote"],
            ["devops"],
            ["aws", "docker", "terraform"],
            ["linkedin.com"],
        )
        job = score_job(parse_message(message)[0], config)
        database = Database(root / "jobs.db")
        assert len(database.save_jobs([job])) == 1
        assert len(database.save_jobs([job])) == 0
        assert write_report([job], root).exists()
        vault = TokenVault(root / "token.key")
        assert vault.decrypt(vault.encrypt("secret")) == "secret"
        return {
            "parser": "pass",
            "scoring": "pass",
            "deduplication": "pass",
            "excel": "pass",
            "encryption": "pass",
        }
