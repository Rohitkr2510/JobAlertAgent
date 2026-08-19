# Security policy

Do not open a public issue containing credentials, OAuth tokens, personal email content, or vulnerability details. Use GitHub's private vulnerability reporting feature when it is available for this repository.

Supported security updates target the latest tagged release. Every change is checked by CodeQL, Bandit, pip-audit, Gitleaks, Hadolint, Trivy, tests, and container smoke tests before release.

JobAlertAgent never needs a Gmail password. OAuth client files, refresh tokens, encryption keys, exported email, SQLite data, and reports must remain outside Git and are excluded by `.gitignore` and `.dockerignore`.
