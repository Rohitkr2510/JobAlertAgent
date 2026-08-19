import hashlib
import logging
from datetime import UTC, datetime

from jobalert.account_manager import AccountManager
from jobalert.config import Config
from jobalert.database import Database
from jobalert.gmail_client import fetch_messages_with_credentials
from jobalert.parser import parse_message
from jobalert.scoring import is_recent, score_job

LOGGER = logging.getLogger(__name__)


def sync_account(
    email: str, manager: AccountManager, database: Database, config: Config
) -> dict[str, int | str]:
    started = datetime.now(UTC).isoformat()
    messages = 0
    jobs = []
    try:
        credentials = manager.credentials(email)
        for message in fetch_messages_with_credentials(
            credentials, config.hours, config.sender_domains
        ):
            messages += 1
            for job in parse_message(message):
                job.account_email = email
                if is_recent(job, config):
                    jobs.append(score_job(job, config))
        fresh = database.save_jobs(jobs)
        with database.connect() as connection:
            connection.execute(
                "UPDATE accounts SET last_sync = ?, last_error = NULL WHERE email = ?",
                (datetime.now(UTC).isoformat(), email),
            )
            connection.execute(
                """INSERT INTO runs
                (started_at, account_email, emails_processed, jobs_found, new_jobs, status)
                VALUES (?, ?, ?, ?, ?, 'success')""",
                (started, email, messages, len(jobs), len(fresh)),
            )
        account_id = hashlib.sha256(email.lower().encode()).hexdigest()[:12]
        LOGGER.info(
            "gmail_sync_completed account_id=%s emails=%s jobs=%s new=%s",
            account_id,
            messages,
            len(jobs),
            len(fresh),
        )
        return {"account": email, "emails": messages, "jobs": len(jobs), "new": len(fresh)}
    except Exception as error:
        with database.connect() as connection:
            connection.execute(
                "UPDATE accounts SET last_error = ? WHERE email = ?", (str(error), email)
            )
            connection.execute(
                """INSERT INTO runs
                (started_at, account_email, status, error) VALUES (?, ?, 'failed', ?)""",
                (started, email, str(error)),
            )
        account_id = hashlib.sha256(email.lower().encode()).hexdigest()[:12]
        LOGGER.exception("gmail_sync_failed account_id=%s", account_id)
        raise
