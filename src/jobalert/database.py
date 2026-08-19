import sqlite3
from pathlib import Path

from jobalert.models import Job


def save_new(jobs: list[Job], path: Path) -> list[Job]:
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path)
    connection.execute(
        "CREATE TABLE IF NOT EXISTS jobs (unique_id TEXT PRIMARY KEY, url TEXT, first_seen TEXT)"
    )
    fresh: list[Job] = []
    for job in jobs:
        cursor = connection.execute(
            "INSERT OR IGNORE INTO jobs VALUES (?, ?, ?)",
            (job.unique_id, job.url, job.email_received_at.isoformat()),
        )
        if cursor.rowcount:
            fresh.append(job)
    connection.commit()
    connection.close()
    return fresh
