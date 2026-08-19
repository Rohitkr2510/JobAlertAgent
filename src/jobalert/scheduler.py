import logging
import os
from datetime import datetime
from zoneinfo import ZoneInfo

from apscheduler.schedulers.background import BackgroundScheduler

from jobalert.account_manager import AccountManager
from jobalert.config import load_config
from jobalert.database import Database
from jobalert.sync import sync_account

LOGGER = logging.getLogger(__name__)


def scheduled_tick(database: Database, manager: AccountManager, config_path) -> None:
    if database.setting("schedule_enabled", "false") != "true":
        return
    timezone = ZoneInfo(os.getenv("JOBALERT_TIMEZONE", "Asia/Kolkata"))
    now = datetime.now(timezone)
    if now.strftime("%H:%M") != database.setting("schedule_time", "08:00"):
        return
    today = now.date().isoformat()
    if database.setting("last_schedule_date") == today:
        return
    database.set_setting("last_schedule_date", today)
    config = load_config(config_path)
    for account in database.rows("accounts"):
        if account["enabled"]:
            try:
                sync_account(account["email"], manager, database, config)
            except Exception:
                LOGGER.exception("scheduled_sync_failed")


def start_scheduler(database: Database, manager: AccountManager, config_path):
    scheduler = BackgroundScheduler(daemon=True)
    scheduler.add_job(
        scheduled_tick,
        "interval",
        minutes=1,
        args=[database, manager, config_path],
        max_instances=1,
        coalesce=True,
    )
    scheduler.start()
    return scheduler
