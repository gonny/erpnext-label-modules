# Label Calculator — ERPNext v16 Custom App

> A modular label price calculator for self-adhesive labels, integrated into
> ERPNext's sales workflow (Quotation → Sales Order → Invoice).

## Quickstart (DevContainer)

**Requirements:** Docker Desktop, VS Code with the
[Dev Containers](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)
extension.

```bash
# 1. Clone the repo
git clone https://github.com/gonny/erpnext-label-modules.git
cd erpnext-label-modules

# 2. Open in VS Code
code .

# 3. When prompted, click "Reopen in Container"
#    The post-create script runs automatically (≈ 3–5 min on first run)

# 4. Start the development server inside the container
cd /workspace/frappe-bench
bench start
```

Open [http://development.localhost:8000](http://development.localhost:8000)
— log in with **Administrator / admin**.

## Architecture Overview

```
erpnext-label-modules/
├── .devcontainer/          # VS Code DevContainer (MariaDB, Redis, Frappe bench)
├── .github/
│   ├── workflows/          # GitHub Actions CI/CD
│   ├── mcp.json            # MCP tools configuration for AI agents
│   └── dependabot.yml      # Automated dependency updates
├── apps/
│   └── label_calculator/   # The custom Frappe app
│       └── label_calculator/
│           ├── core/       # Pure Python engine — zero Frappe imports
│           ├── api/        # @frappe.whitelist() REST endpoints
│           ├── label_calculator/doctype/  # Frappe DocType definitions
│           ├── tests/      # pytest unit + integration tests
│           └── templates/  # Jinja print-format templates
├── docs/                   # Project documentation
├── pyproject.toml          # Repo-level ruff / mypy / pytest config
└── README.md
```

### Key Design Decisions

| Concern | Decision |
|---|---|
| **Separation of concerns** | `core/` is pure Python, testable without Frappe |
| **Framework** | Frappe v16 / ERPNext v16 CE |
| **Currency** | CZK — Czech rounding rules |
| **API** | REST-first via `@frappe.whitelist()` in `api/` |
| **Testing** | `pytest -m unit` (fast, no DB) + `bench run-tests` (full) |
| **Linting** | ruff (lint + format), mypy (gradual typing) |
| **AI Agent** | 5 MCP tools — see [docs/mcp-tools.md](docs/mcp-tools.md) |

## Running Tests

```bash
# ── Unit tests (no Frappe, runs anywhere) ──────────────────────────────────
cd apps/label_calculator
pytest -m unit -q

# ── Full integration tests (requires running bench inside devcontainer) ──────
cd /workspace/frappe-bench
bench run-tests --app label_calculator
```

## Linting & Type Checking

```bash
cd apps/label_calculator
ruff check .               # lint
ruff format --check .      # format
mypy label_calculator/     # type check
```

## Pre-commit Hooks

```bash
pip install pre-commit
pre-commit install          # installs git hooks
pre-commit run --all-files  # run all hooks manually
```

## Documentation

| Document | Purpose |
|---|---|
| [CONTRIBUTING.md](CONTRIBUTING.md) | Branch strategy, commit convention, PR checklist |
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | High-level architecture |
| [docs/mcp-tools.md](docs/mcp-tools.md) | MCP tools for AI agent development |
| [docs/AGENT_GUIDELINES.md](docs/AGENT_GUIDELINES.md) | AI agent mindset and coding conventions |
| [docs/BACKLOG.md](docs/BACKLOG.md) | Future items explicitly out of scope |

## License

MIT — see [LICENSE](LICENSE).
