# Rollback plan

1. Stop the current ReleaseGuard container.
2. Start the previously tagged image: `docker run releaseguard:<previous-version>`.
3. Confirm `GET /health` returns `{"status":"ok"}`.
4. Preserve the failed report for audit and diagnosis.

