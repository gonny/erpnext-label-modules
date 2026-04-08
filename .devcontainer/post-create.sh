#!/usr/bin/env bash
# post-create.sh — Automated devcontainer setup for label_calculator
# Based on official frappe_docker development setup.
# Run once after the container is created. Idempotent.
set -euo pipefail

FRAPPE_BRANCH="${FRAPPE_BRANCH:-version-16}"
ERPNEXT_BRANCH="${ERPNEXT_BRANCH:-version-16}"
SITE_NAME="development.localhost"
BENCH_DIR="/workspaces/erpnext-label-modules/frappe-bench"
APP_SRC="/workspaces/erpnext-label-modules"

# ── [0/8] Fix permissions ──────────────────────────────────────────
echo ">>> [0/8] Fixing workspace permissions"
sudo chown -R frappe:frappe $APP_SRC
git config --global user.email "snobljan@gmail.com"
git config --global user.name "Snobljan"

# ── [1/8] Init bench ───────────────────────────────────────────────
echo ">>> [1/8] Initialising bench (Frappe ${FRAPPE_BRANCH})"
if [ ! -d "${BENCH_DIR}" ]; then
  bench init \
    --frappe-branch "${FRAPPE_BRANCH}" \
    --skip-redis-config-generation \
    --verbose \
    "${BENCH_DIR}"
fi

cd "${BENCH_DIR}"

# ── [2/8] Configure services ──────────────────────────────────────
echo ">>> [2/8] Configuring services"
bench set-config -g db_host 127.0.0.1
bench set-config -g db_port 3306
bench set-config -g redis_cache "redis://127.0.0.1:6379"
bench set-config -g redis_queue "redis://127.0.0.1:6381"
bench set-config -g redis_socketio "redis://127.0.0.1:6381"
bench set-config -g developer_mode 1

# ── [3/8] Get ERPNext ─────────────────────────────────────────────
echo ">>> [3/8] Getting ERPNext app (${ERPNEXT_BRANCH})"
if [ ! -d "apps/erpnext" ]; then
  bench get-app --branch "${ERPNEXT_BRANCH}" erpnext
fi

# ── [4/8] Link label_calculator ───────────────────────────────────
echo ">>> [4/8] Linking label_calculator app"
if [ ! -d "apps/label_calculator" ]; then
  ln -s "${APP_SRC}/apps/label_calculator" apps/label_calculator
fi
# Install in editable mode so Frappe sees it
if ! bench pip show label_calculator &>/dev/null; then
  bench pip install -e apps/label_calculator
fi

# ── [5/8] Create site ────────────────────────────────────────────
echo ">>> [5/8] Creating development site"
if [ ! -d "sites/${SITE_NAME}" ]; then
  bench new-site \
    --db-root-username root \
    --db-root-password "123" \
    --admin-password admin \
    --mariadb-user-host-login-scope='%' \
    "${SITE_NAME}"
fi

bench use "${SITE_NAME}"

# ── [6/8] Install apps ───────────────────────────────────────────
echo ">>> [6/8] Installing apps on site"
bench --site "${SITE_NAME}" install-app erpnext || true
bench --site "${SITE_NAME}" install-app label_calculator || true

# ── [7/8] Build & migrate ────────────────────────────────────────
echo ">>> [7/8] Building assets & migrating"
bench build --app frappe
bench --site "${SITE_NAME}" migrate

# ── [8/8] Dev tools ──────────────────────────────────────────────
echo ">>> [8/8] Installing Python dev tools"
pip install --quiet --user \
  pre-commit \
  pip-audit \
  pytest-cov
# Note: ruff, mypy, pytest are pre-installed in frappe/bench image
# Note: frappe-mcp excluded — incompatible with Python 3.14 (pydantic-core)
#       Use shell MCP + bench console instead. Tracked in BACKLOG.

echo ""
echo "✅  Setup complete!"
echo "   Run: cd ${BENCH_DIR} && bench start"
echo "   Open: http://localhost:8000 — login: Administrator / admin"
