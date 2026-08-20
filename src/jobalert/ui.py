import os
from pathlib import Path
from urllib.parse import urlencode

import pandas as pd
import streamlit as st
import yaml

from jobalert.account_manager import AccountManager
from jobalert.config import load_config
from jobalert.database import Database
from jobalert.report import write_report
from jobalert.scheduler import start_scheduler
from jobalert.selfcheck import run_self_check
from jobalert.sync import sync_account
from jobalert.token_store import TokenVault

ROOT = Path(os.getenv("JOBALERT_ROOT", "."))
DB_PATH = ROOT / os.getenv("JOBALERT_DATABASE", "data/jobs.db")
CONFIG_PATH = ROOT / os.getenv("JOBALERT_CONFIG", "config/job-filters.yaml")
WEB_CREDENTIALS = ROOT / os.getenv("JOBALERT_WEB_CREDENTIALS", "secrets/web_credentials.json")
KEY_PATH = ROOT / os.getenv("JOBALERT_TOKEN_KEY", "secrets/token.key")
REDIRECT_URI = os.getenv("JOBALERT_REDIRECT_URI", "http://localhost:8501")


@st.cache_resource
def services():
    database = Database(DB_PATH)
    manager = AccountManager(database, TokenVault(KEY_PATH))
    start_scheduler(database, manager, CONFIG_PATH)
    return database, manager


def metrics(database: Database) -> None:
    jobs = database.rows("jobs")
    accounts = database.rows("accounts")
    high = sum(job["priority"] == "High Priority" for job in jobs)
    applied = sum(job["application_status"] == "Applied" for job in jobs)
    columns = st.columns(4)
    columns[0].metric("Connected accounts", len(accounts))
    columns[1].metric("Jobs collected", len(jobs))
    columns[2].metric("High priority", high)
    columns[3].metric("Applied", applied)


def accounts_page(database: Database, manager: AccountManager) -> None:
    st.subheader("Gmail accounts")
    st.caption("Every mailbox owner must approve Google's read-only OAuth consent screen.")
    if "code" in st.query_params and "state" in st.query_params:
        try:
            expected_state = database.setting("oauth_state")
            if not expected_state or st.query_params["state"] != expected_state:
                raise ValueError("OAuth state mismatch; start the connection again.")
            current = REDIRECT_URI + "?" + urlencode(st.query_params.to_dict())
            code_verifier = database.setting("oauth_code_verifier")

            email = manager.complete_authorization(
                WEB_CREDENTIALS,
                REDIRECT_URI,
                current,
                st.query_params["state"],
                code_verifier,
            )
            database.set_setting("oauth_code_verifier", "")
            database.set_setting("oauth_state", "")
            st.query_params.clear()
            st.success(f"Connected {email}")
        except Exception as error:
            st.error(f"Authorization failed: {error}")

    with st.form("connect-account"):
        email_hint = st.text_input("Gmail address", placeholder="name@gmail.com")
        connect = st.form_submit_button("Connect Gmail account", type="primary")
    if connect:
        if not WEB_CREDENTIALS.exists():
            st.error("Add secrets/web_credentials.json before connecting an account.")
        elif "@" not in email_hint:
            st.error("Enter a valid email address.")
        else:
            url, state, code_verifier = manager.authorization_url(WEB_CREDENTIALS, REDIRECT_URI, email_hint)
            database.set_setting("oauth_state", state)
            database.set_setting("oauth_code_verifier", code_verifier)
            st.link_button("Continue securely with Google", url, type="primary")

    for account in database.rows("accounts"):
        with st.container(border=True):
            left, middle, right = st.columns([3, 2, 2])
            left.write(f"**{account['email']}**")
            left.caption(f"Last sync: {account['last_sync'] or 'Never'}")
            enabled = middle.toggle(
                "Enabled", value=bool(account["enabled"]), key=f"enabled-{account['account_id']}"
            )
            manager.set_enabled(account["email"], enabled)
            if right.button("Sync now", key=f"sync-{account['account_id']}"):
                with st.spinner(f"Scanning {account['email']}..."):
                    try:
                        result = sync_account(
                            account["email"], manager, database, load_config(CONFIG_PATH)
                        )
                        st.success(
                            f"Processed {result['emails']} emails; added {result['new']} jobs."
                        )
                    except Exception as error:
                        st.error(str(error))
            if account["last_error"]:
                st.error(account["last_error"])
            confirm = st.checkbox("Confirm removal", key=f"confirm-remove-{account['account_id']}")
            if st.button(
                "Remove local access",
                key=f"remove-{account['account_id']}",
                disabled=not confirm,
            ):
                manager.remove(account["email"])
                st.rerun()


def jobs_page(database: Database) -> None:
    st.subheader("Jobs")
    jobs = database.rows("jobs")
    if not jobs:
        st.info("No jobs collected yet. Connect Gmail or run the offline self-check.")
        return
    frame = pd.DataFrame(jobs)
    account_options = ["All", *sorted(frame["account_email"].dropna().unique())]
    source_options = ["All", *sorted(frame["source"].dropna().unique())]
    col1, col2, col3 = st.columns(3)
    account = col1.selectbox("Account", account_options)
    source = col2.selectbox("Source", source_options)
    minimum = col3.slider("Minimum score", 0, 100, 60)
    if account != "All":
        frame = frame[frame["account_email"] == account]
    if source != "All":
        frame = frame[frame["source"] == source]
    frame = frame[frame["score"] >= minimum]
    st.dataframe(
        frame[
            [
                "score",
                "priority",
                "title",
                "company",
                "location",
                "experience",
                "source",
                "account_email",
                "application_status",
                "url",
            ]
        ],
        column_config={"url": st.column_config.LinkColumn("Job link")},
        hide_index=True,
        use_container_width=True,
    )
    with st.expander("Update application status"):
        selected = st.selectbox(
            "Job",
            options=frame["unique_id"].tolist(),
            format_func=lambda value: frame.loc[frame["unique_id"] == value, "title"].iloc[0],
        )
        status = st.selectbox(
            "Status", ["New", "Saved", "Applied", "Interview", "Offer", "Rejected"]
        )
        if st.button("Update status"):
            database.update_job_status(selected, status)
            st.success("Application status updated.")
            st.rerun()
    if st.button("Generate Excel report"):
        from jobalert.models import Job

        report_jobs = []
        for row in frame.to_dict("records"):
            job = Job(
                row["title"],
                row["company"],
                row["location"],
                row["url"],
                row["source"],
                pd.to_datetime(row["email_received_at"]).to_pydatetime(),
                experience=row["experience"],
                score=row["score"],
                priority=row["priority"],
                reason=row["reason"],
                account_email=row["account_email"],
                application_status=row["application_status"],
            )
            job.skills = (row["skills"] or "").split(", ")
            report_jobs.append(job)
        path = write_report(report_jobs, ROOT / "reports")
        st.success(f"Created {path}")


def app() -> None:
    st.set_page_config(page_title="JobAlertAgent", page_icon="📡", layout="wide")
    database, manager = services()
    st.title("📡 JobAlertAgent")
    st.caption("Local, multi-account Gmail job intelligence—without an LLM.")
    metrics(database)
    dashboard, accounts, jobs, tracker, logs, settings = st.tabs(
        ["Dashboard", "Email Accounts", "Jobs", "Applications", "Activity", "Settings"]
    )
    with dashboard:
        if st.button("Sync all enabled accounts", type="primary"):
            for account in database.rows("accounts"):
                if account["enabled"]:
                    with st.spinner(account["email"]):
                        try:
                            sync_account(
                                account["email"], manager, database, load_config(CONFIG_PATH)
                            )
                        except Exception as error:
                            st.error(f"{account['email']}: {error}")
            st.rerun()
        recent = pd.DataFrame(database.rows("jobs", 20))
        if not recent.empty:
            st.dataframe(
                recent[["score", "title", "company", "source", "account_email", "url"]],
                column_config={"url": st.column_config.LinkColumn("Job link")},
                hide_index=True,
                use_container_width=True,
            )
    with accounts:
        accounts_page(database, manager)
    with jobs:
        jobs_page(database)
    with tracker:
        data = pd.DataFrame(database.rows("jobs"))
        if data.empty:
            st.info("No applications yet.")
        else:
            st.bar_chart(data["application_status"].value_counts())
    with logs:
        runs = pd.DataFrame(database.rows("runs", 200))
        st.dataframe(runs, hide_index=True, use_container_width=True)
    with settings:
        st.write(f"Database: `{DB_PATH}`")
        st.write(f"Filter configuration: `{CONFIG_PATH}`")
        st.write(f"OAuth redirect: `{REDIRECT_URI}`")
        current = load_config(CONFIG_PATH)
        with st.form("filter-settings"):
            hours = st.number_input("Email age in hours", 1, 168, current.hours)
            minimum_score = st.slider("Minimum score", 0, 100, current.minimum_score)
            maximum_experience = st.number_input(
                "Maximum experience", 1, 20, current.maximum_experience_years
            )
            roles = st.text_area("Target roles (one per line)", "\n".join(current.role_keywords))
            skills = st.text_area("Skills (one per line)", "\n".join(current.skill_keywords))
            locations = st.text_area(
                "Preferred locations (one per line)", "\n".join(current.preferred_locations)
            )
            if st.form_submit_button("Save filters"):
                payload = {
                    "hours": int(hours),
                    "minimum_score": int(minimum_score),
                    "high_priority_score": current.high_priority_score,
                    "maximum_experience_years": int(maximum_experience),
                    "preferred_locations": [
                        line.strip() for line in locations.splitlines() if line.strip()
                    ],
                    "role_keywords": [line.strip() for line in roles.splitlines() if line.strip()],
                    "skill_keywords": [
                        line.strip() for line in skills.splitlines() if line.strip()
                    ],
                    "sender_domains": current.sender_domains,
                }
                CONFIG_PATH.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")
                st.success("Filters saved.")
        with st.form("schedule-settings"):
            schedule_enabled = st.toggle(
                "Enable daily automatic scan",
                value=database.setting("schedule_enabled", "false") == "true",
            )
            schedule_time = st.text_input(
                "Daily time (local HH:MM)", database.setting("schedule_time", "08:00")
            )
            if st.form_submit_button("Save schedule"):
                database.set_setting("schedule_enabled", str(schedule_enabled).lower())
                database.set_setting("schedule_time", schedule_time)
                st.success("Schedule saved.")
        if st.button("Run offline functional self-check"):
            st.json(run_self_check())


if __name__ == "__main__":
    app()
