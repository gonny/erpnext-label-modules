# Label Calculator

> A custom Frappe/ERPNext v16 app for calculating prices of self-adhesive labels.

## Quickstart (DevContainer)

**Requirements:** Docker Desktop, VS Code with the Dev Containers extension.

```bash
git clone https://github.com/gonny/erpnext-label-modules.git
cd erpnext-label-modules
code .
# VS Code will prompt: "Reopen in Container" — click it
# Post-create script runs automatically (≈ 3–5 minutes on first run)
```

Once the container is ready:

```bash
cd /workspace/frappe-bench
bench start
```

Open [http://development.localhost:8000](http://development.localhost:8000)
and log in with **Administrator / admin**.

## Architecture Overview

```
erpnext-label-modules/
├── .devcontainer/          # VS Code DevContainer configuration
├── .github/
│   ├── workflows/          # GitHub Actions CI pipeline
│   └── mcp.json            # MCP tools for AI-agent development
├── apps/
│   └── label_calculator/   # Custom Frappe app (this is the product)
│       └── label_calculator/
│           ├── core/       # Pure Python calculation engine (no Frappe deps)
│           ├── api/        # Whitelisted API methods
│           ├── label_calculator/doctype/  # Frappe DocType definitions
│           ├── tests/      # Unit + integration tests
│           └── templates/  # Jinja print format templates
├── docs/                   # Project documentation
└── README.md
```

### Key Design Decisions

| Concern | Decision |
|---|---|
| **Separation of concerns** | `core/` is pure Python — testable without Frappe |
| **Framework** | Frappe v16 / ERPNext v16 CE only |
| **Currency** | CZK (Czech Koruna) with Czech rounding rules |
| **API** | REST-first via `@frappe.whitelist()` in `api/` |
| **Testing** | `pytest -m unit` (fast) + `bench run-tests` (integration) |

## Running Tests

```bash
# Unit tests only (no Frappe running required)
cd apps/label_calculator
pytest -m unit

# Full integration tests (requires running bench)
cd /workspace/frappe-bench
bench run-tests --app label_calculator
```

## Linting

```bash
cd apps/label_calculator
ruff check .
ruff format --check .
mypy label_calculator/
```

## Pre-commit Hooks

```bash
pip install pre-commit
pre-commit install
pre-commit run --all-files
```

## Documentation

| File | Purpose |
|---|---|
| [CONTRIBUTING.md](CONTRIBUTING.md) | Branch strategy, commit conventions, PR checklist |
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | High-level architecture |
| [docs/mcp-tools.md](docs/mcp-tools.md) | MCP tools inventory and usage |
| [docs/AGENT_GUIDELINES.md](docs/AGENT_GUIDELINES.md) | AI agent mindset and conventions |
| [docs/BACKLOG.md](docs/BACKLOG.md) | Future items explicitly out of scope |

## License

MIT — see [LICENSE](LICENSE).
