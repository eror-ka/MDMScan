#!/usr/bin/env bash
set -euo pipefail

mkdir -p "${SCAN_WORKDIR:-/tmp/scans}"

echo "[entrypoint] starting Celery worker"
exec celery -A app.tasks worker \
    --loglevel="${CELERY_LOGLEVEL:-INFO}" \
    --concurrency="${CELERY_CONCURRENCY:-2}" \
    --without-gossip --without-mingle
