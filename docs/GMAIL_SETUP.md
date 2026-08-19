# Free Gmail OAuth setup

JobAlertAgent uses the official Gmail API with the read-only scope. Google does not charge for this normal personal automation setup. The app can read messages but cannot send, delete, label, or modify them.

## 1. Create the Google Cloud project

1. Sign in to Google Cloud Console.
2. Create a project named `JobAlertAgent`.
3. Open **APIs & Services → Library**.
4. Find **Gmail API** and click **Enable**.

## 2. Configure Google Auth Platform

1. Open **Google Auth Platform → Branding** and enter `JobAlertAgent` as the app name.
2. Select your own Gmail address for support/contact email.
3. In **Audience**, use **External** for a normal personal Gmail account. Use **Internal** only when you have an eligible Google Workspace organization.
4. Keep the app in testing mode.
5. Add your Gmail address under **Test users**.

You do not need to publish or verify the app when it is only for your own test-user account.

## 3. Create the OAuth client

1. Open **Google Auth Platform → Clients**.
2. Click **Create client**.
3. Choose **Desktop app**.
4. Name it `JobAlertAgent Desktop`.
5. Download the JSON file.
6. Rename it to `credentials.json` and place it in the local `secrets/` directory.

### Dashboard and multiple accounts

For the web dashboard, create a second OAuth client of type **Web application**:

1. Add `http://localhost:8501` under **Authorized redirect URIs**.
2. Download the client JSON.
3. Save it as `secrets/web_credentials.json`.
4. Start the dashboard and use **Email Accounts → Connect Gmail account**.

The email address entered in the dashboard is only a login hint. JobAlertAgent verifies and stores the address returned by Google after consent. Each connected account receives its own encrypted local token.

Do not upload this file to GitHub. The repository's `.gitignore` already excludes `secrets/`.

## 4. Authorize once

Native Python:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[gmail]'
jobalert gmail-auth \
  --credentials secrets/credentials.json \
  --token secrets/token.json
```

Windows PowerShell activation:

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
pip install -e ".[gmail]"
jobalert gmail-auth --credentials secrets/credentials.json --token secrets/token.json
```

A browser opens. Sign in with the Gmail address added as a test user and approve read-only access. The resulting `token.json` is also secret and must remain inside `secrets/`.

## 5. Test collection

Make sure LinkedIn, Indeed, and Naukri job alerts are already arriving in Gmail, then run:

```bash
jobalert collect-gmail \
  --credentials secrets/credentials.json \
  --token secrets/token.json \
  --config config/job-filters.yaml \
  --database data/jobs.db \
  --output reports
```

The workbook appears in `reports/daily-jobs-YYYY-MM-DD.xlsx`. Run it a second time to confirm SQLite prevents duplicate jobs.

## 6. Run with Docker

Perform the first browser authorization natively. After `token.json` exists:

```bash
docker compose run --rm --entrypoint jobalert jobalert collect-gmail \
  --credentials /app/secrets/credentials.json \
  --token /app/secrets/token.json \
  --config /app/config/job-filters.yaml \
  --database /app/data/jobs.db \
  --output /app/reports
```

## Troubleshooting

- **Access blocked / app not verified:** confirm the app is in testing and your Gmail address is a test user.
- **Credentials file not found:** confirm the file is `secrets/credentials.json` relative to the repository.
- **No jobs found:** confirm alert emails arrived within 24 hours and sender domains match `config/job-filters.yaml`.
- **Token scope changed:** delete only your local `secrets/token.json` and authorize again.
