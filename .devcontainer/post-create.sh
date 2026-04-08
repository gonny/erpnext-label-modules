#!/usr/bin/env bash
# post-create.sh — Automated devcontainer setup for label_calculator
# Run once after the container is created. Idempotent.
set -euo pipefail

FRAPPE_BRANCH="${FRAPPE_BRANCH:-version-16}"
ERPNEXT_BRANCH="${ERPNEXT_BRANCH:-version-16}"
SITE_NAME="development.localhost"
BENCH_DIR="/workspace/frappe-bench"
APP_REPO="/workspace/apps/label_calculator"

echo ">>> [1/8] Initialising bench (Frappe ${FRAPPE_BRANCH})"
if [ ! -d "${BENCH_DIR}" ]; then
  bench init \
    --frappe-branch "${FRAPPE_BRANCH}" \
    --skip-redis-config-generation \
    --verbose \
    "${BENCH_DIR}"
fi

cd "${BENCH_DIR}"

echo ">>> [2/8] Configuring services"
bench set-config -g db_host mariadb
bench set-config -g db_port 3306
bench set-config -g redis_cache "redis://redis-cache:6379"
bench set-config -g redis_queue "redis://redis-queue:6379"
bench set-config -g redis_socketio "redis://redis-queue:6379"
bench set-config -g developer_mode 1

echo ">>> [3/8] Getting ERPNext app (${ERPNEXT_BRANCH})"
if [ ! -d "apps/erpnext" ]; then
  bench get-app --branch "${ERPNEXT_BRANCH}" erpnext
fi

echo ">>> [4/8] Linking label_calculator app"
if [ ! -d "apps/label_calculator" ]; then
  ln -s "${APP_REPO}" apps/label_calculator
fi

echo ">>> [5/8] Creating development site"
if [ ! -d "sites/${SITE_NAME}" ]; then
  bench new-site \
    --db-root-password "${MYSQL_ROOT_PASSWORD:-admin}" \
    --admin-password admin \
    --no-mariadb-socket \
    "${SITE_NAME}"
fi

bench use "${SITE_NAME}"

echo ">>> [6/8] Installing apps on site"
bench --site "${SITE_NAME}" install-app erpnext || true
bench --site "${SITE_NAME}" install-app label_calculator || true

echo ">>> [7/8] Building assets & migrating"
bench build --app frappe
bench --site "${SITE_NAME}" migrate

echo ">>> [8/8] Installing Python dev tools"
pip install --quiet \
  ruff \
  mypy \
  pre-commit \
  pip-audit \
  pytest \
  pytest-cov \
  frappe-mcp

echo ""
echo "✅  Setup complete!"
echo "   Run: cd ${BENCH_DIR} && bench start"
echo "   Open: http://${SITE_NAME}:8000 — login: Administrator / admin"
