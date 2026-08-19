import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

from jobalert.models import Job


class Database:
    def __init__(self, path: Path):
        self.path = path
        path.parent.mkdir(parents=True, exist_ok=True)
        self.initialize()

    @contextmanager
    def connect(self) -> Iterator[sqlite3.Connection]:
        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        try:
            yield connection
            connection.commit()
        finally:
            connection.close()

    def initialize(self) -> None:
        with self.connect() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS accounts (
                    account_id TEXT PRIMARY KEY,
                    email TEXT UNIQUE NOT NULL,
                    token_encrypted BLOB NOT NULL,
                    enabled INTEGER NOT NULL DEFAULT 1,
                    created_at TEXT NOT NULL,
                    last_sync TEXT,
                    last_error TEXT
                );
                CREATE TABLE IF NOT EXISTS jobs (
                    unique_id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    company TEXT,
                    location TEXT,
                    experience TEXT,
                    skills TEXT,
                    posted_at TEXT,
                    email_received_at TEXT NOT NULL,
                    source TEXT,
                    account_email TEXT,
                    url TEXT,
                    score INTEGER,
                    priority TEXT,
                    date_verified INTEGER,
                    application_status TEXT NOT NULL DEFAULT 'New',
                    reason TEXT,
                    first_seen TEXT NOT NULL,
                    raw_context TEXT
                );
                CREATE TABLE IF NOT EXISTS runs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    started_at TEXT NOT NULL,
                    account_email TEXT,
                    emails_processed INTEGER DEFAULT 0,
                    jobs_found INTEGER DEFAULT 0,
                    new_jobs INTEGER DEFAULT 0,
                    status TEXT NOT NULL,
                    error TEXT
                );
                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                );
                """
            )

    def save_jobs(self, jobs: list[Job]) -> list[Job]:
        fresh: list[Job] = []
        with self.connect() as connection:
            for job in jobs:
                cursor = connection.execute(
                    """INSERT OR IGNORE INTO jobs VALUES
                    (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (
                        job.unique_id,
                        job.title,
                        job.company,
                        job.location,
                        job.experience,
                        ", ".join(job.skills),
                        job.posted_at.isoformat() if job.posted_at else None,
                        job.email_received_at.isoformat(),
                        job.source,
                        job.account_email,
                        job.url,
                        job.score,
                        job.priority,
                        int(job.date_verified),
                        job.application_status,
                        job.reason,
                        job.email_received_at.isoformat(),
                        job.text[:4000],
                    ),
                )
                if cursor.rowcount:
                    fresh.append(job)
        return fresh

    def rows(self, table: str, limit: int = 1000) -> list[dict]:
        if table not in {"accounts", "jobs", "runs"}:
            raise ValueError("Unsupported table")
        with self.connect() as connection:
            rows = connection.execute(
                f"SELECT * FROM {table} ORDER BY rowid DESC LIMIT ?", (limit,)
            ).fetchall()
        return [dict(row) for row in rows]

    def update_job_status(self, unique_id: str, status: str) -> None:
        allowed = {"New", "Saved", "Applied", "Interview", "Offer", "Rejected"}
        if status not in allowed:
            raise ValueError("Invalid application status")
        with self.connect() as connection:
            connection.execute(
                "UPDATE jobs SET application_status = ? WHERE unique_id = ?",
                (status, unique_id),
            )

    def setting(self, key: str, default: str = "") -> str:
        with self.connect() as connection:
            row = connection.execute("SELECT value FROM settings WHERE key = ?", (key,)).fetchone()
        return row["value"] if row else default

    def set_setting(self, key: str, value: str) -> None:
        with self.connect() as connection:
            connection.execute(
                """INSERT INTO settings (key, value) VALUES (?, ?)
                ON CONFLICT(key) DO UPDATE SET value=excluded.value""",
                (key, value),
            )


def save_new(jobs: list[Job], path: Path) -> list[Job]:
    return Database(path).save_jobs(jobs)
