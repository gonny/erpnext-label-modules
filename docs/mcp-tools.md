# MCP Tools

This project configures **5 MCP servers** for AI agent development.
Configuration lives in `.github/mcp.json`.

## Tool Inventory

### 1. `github` — Repository Management

**Package:** `@modelcontextprotocol/server-github`

**Purpose:** Manage issues, pull requests, branches, and GitHub metadata.

**When to use:**
- Reading issue details before starting work
- Creating PRs with proper descriptions
- Checking CI run status
- Listing open issues/PRs

**Example:**
```
List open issues in gonny/erpnext-label-modules
```

---

### 2. `filesystem` — Codebase Navigation

**Package:** `@modelcontextprotocol/server-filesystem`

**Workspace root:** `/workspace`

**Purpose:** Read and write files in the repository and Frappe source.

**When to use:**
- Reading source files to understand current implementation
- Writing new files or modifying existing ones
- Navigating the Frappe source code as documentation (when `context7` lacks detail)

**Example:**
```
Read /workspace/apps/label_calculator/label_calculator/core/calculator.py
```

---

### 3. `shell` — Primary Workhorse

**Package:** `@modelcontextprotocol/server-shell`

**Purpose:** Execute allowed CLI commands — the Swiss army knife.

**Allowed commands:** `bench`, `pytest`, `ruff`, `mypy`, `pre-commit`,
`pip`, `pip-audit`, `curl`, `cat`, `ls`, `find`, `grep`, `echo`, `pwd`, `cd`

**When to use — examples:**

| Task | Command |
|---|---|
| Run unit tests | `pytest -m unit` |
| Lint check | `ruff check apps/label_calculator/` |
| Type check | `mypy apps/label_calculator/label_calculator/` |
| Integration tests | `bench run-tests --app label_calculator` |
| DB query | `bench console` then Python |
| API health check | `curl http://development.localhost:8000/api/method/frappe.ping` |
| Check bench version | `bench --version` |
| DB direct query | `bench mariadb` |

---

### 4. `context7` — Library Documentation

**Package:** `@upstash/context7-mcp`

**Purpose:** Fetch up-to-date API documentation for Frappe Framework,
ERPNext, and Python libraries.

**When to use:**
- "What is the correct API for `frappe.get_doc()`?"
- "How does `frappe.whitelist()` work in v16?"
- "What are the available hooks in hooks.py?"
- Researching any Frappe/Python pattern before implementing it

**Do NOT use web search** — this tool replaces it for documentation lookups.

---

### 5. `frappe-mcp` — Frappe Instance Interaction

**Package:** `frappe-mcp` (Python, installed via pip)

**Environment variables needed:**
- `FRAPPE_URL` — defaults to `http://development.localhost:8000`
- `FRAPPE_API_KEY` — generate in Frappe user settings
- `FRAPPE_API_SECRET` — generate in Frappe user settings

**Purpose:** Direct interaction with the running Frappe/ERPNext instance
without manual `bench console` commands.

**When to use:**
- Query DocType metadata (field names, field types, required fields)
- Read or create documents to validate logic
- Validate that an API endpoint returns the expected response
- Check that a migration was applied correctly

**Example:**
```
Get fields of the "Sales Invoice" DocType
List all Label Calculation documents
```

## Setup Notes

1. Ensure the devcontainer is running (`bench start` inside container).
2. Generate API key/secret for the `Administrator` user in
   `Settings → Users → Administrator → API Access`.
3. Set `FRAPPE_API_KEY` and `FRAPPE_API_SECRET` in your `.env` file
   (never commit the actual values — only `.env.example` is committed).
