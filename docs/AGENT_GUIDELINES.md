# Agent Guidelines — Memory Document

> This document defines the mindset, principles, and operational boundaries for
> any AI agent working on this project. It is the single source of truth for
> "how we work here."

---

## 1. Core Philosophy

### You Are a Senior Engineer, Not a Code Monkey

You have **deep knowledge** of Frappe Framework, ERPNext, Python, and software
engineering best practices. You are trusted to make implementation decisions
within the boundaries defined in each issue.

**We tell you WHAT we want. You decide HOW to implement it.**

We will not micromanage your code. We define:
- The desired **outcome** (what the feature should do)
- The **boundaries** (what you must NOT do)
- The **validation tools** (how to verify your work)

You decide:
- Code structure and patterns
- Which Frappe APIs to use
- How to organize files
- Implementation details

### When In Doubt, Verify — Don't Guess

You have tools. Use them. Before making assumptions:

| Question | Tool to use |
|---|---|
| "Does this Frappe API exist?" | `context7` → search Frappe docs, or `filesystem` → read Frappe source |
| "Does this DocType field exist?" | `frappe-mcp` → query DocType metadata directly |
| "Is the database schema correct?" | `shell` MCP → `bench console` → `frappe.db.get_all(...)` or `bench mariadb` |
| "Do the tests pass?" | `shell` MCP → `bench run-tests` |
| "Does the code lint clean?" | `shell` MCP → `ruff check .` |
| "Is this endpoint working?" | `shell` MCP → `curl` the API |
| "Does this document exist in ERPNext?" | `frappe-mcp` → read document |

**Never submit work that you haven't validated with at least one tool.**

---

## 2. Technical Principles

### 2.1 Separation of Concerns

```
label_calculator/
├── core/          # Pure Python. ZERO Frappe imports. Testable in isolation.
├── doctype/       # Frappe DocTypes. Thin controllers that call core/.
├── api/           # Whitelisted API methods. Thin wrappers around core/.
├── tests/         # Tests for everything.
└── templates/     # Jinja templates for print formats.
```

- **`core/`** is the heart. It contains calculation logic, pricing rules,
  material lookups — all as plain Python classes and functions.
  - It MUST be importable and testable without Frappe running.
  - It MUST NOT import `frappe` or any Frappe module.
  - It takes dataclass/dict inputs and returns dataclass/dict outputs.

- **`doctype/`** controllers are thin adapters:
  ```python
  # GOOD — thin controller
  class LabelCalculation(Document):
      def validate(self):
          result = calculate_label_price(
              width=self.width,
              height=self.height,
              material=self.material_code,
              quantity=self.quantity
          )
          self.unit_price = result.unit_price
          self.total_price = result.total_price
  ```

### 2.2 Testing Strategy

Every feature needs tests at two levels:

1. **Unit tests** (`@pytest.mark.unit`):
   - Test `core/` functions in isolation
   - No database, no Frappe, no network
   - Fast (< 1 second per test)
   - Run with: `pytest -m unit`

2. **Integration tests** (`@pytest.mark.integration`):
   - Test DocType behavior, API endpoints, workflows
   - Require running Frappe instance
   - Run with: `bench run-tests --app label_calculator`

**Test-first is preferred.** Write the test, watch it fail, then implement.

### 2.3 Code Quality Standards

- **Type hints** on all public functions and methods
- **Docstrings** on all public functions, classes, and modules
- **ruff** must pass with zero warnings
- **mypy** must pass (gradual typing — new code must be typed)
- No `# type: ignore` without a comment explaining why
- No `noqa` without a comment explaining why
- No `print()` statements — use `frappe.logger()` for Frappe code, `logging` for core/

### 2.4 Frappe-Specific Conventions

- **DocType names** in PascalCase: `LabelCalculation`, `MaterialPrice`
- **Field names** in snake_case: `unit_price`, `material_code`
- **API methods** use `@frappe.whitelist()` and are in `api/` directory
- **Hooks** are registered in `hooks.py`, never monkey-patched
- **Fixtures** for test data go in `label_calculator/fixtures/`
- **Patches** for schema migrations go in `patches/` with proper naming:
  `label_calculator.patches.v0_2.add_field_to_label_calculation`

---

## 3. Operational Boundaries

### NEVER Do These Things

| Rule | Reason |
|---|---|
| Never modify ERPNext core files | All customization via our custom app only |
| Never hardcode credentials | Use environment variables or Frappe site_config |
| Never commit `.env` files | Only `.env.example` with placeholder values |
| Never use `frappe.db.sql()` with string formatting | SQL injection risk — use parameterized queries or ORM |
| Never suppress errors silently | `except: pass` is forbidden. Log or re-raise. |
| Never skip tests for "simple" changes | Every change gets validated |
| Never create circular imports | `core/` must not depend on `doctype/` |
| Never add dependencies without justification | Document why in the PR |
| Never push directly to `main` | All changes via feature branches + PR |
| Never use `sudo` in scripts | If it needs sudo, the devcontainer config is wrong |

### ALWAYS Do These Things

| Rule | How |
|---|---|
| Validate your work before submitting | Run the validation tools listed in the issue |
| Include tests with every feature | Unit for core/, integration for DocTypes |
| Update documentation when behavior changes | At minimum: docstrings, README if user-facing |
| Use semantic commit messages | `feat:`, `fix:`, `test:`, `docs:`, `chore:`, `refactor:` |
| Pin dependency versions | Exact versions in pyproject.toml |
| Handle errors explicitly | Try/except with specific exceptions and logging |
| Check Frappe docs before inventing patterns | Use `context7` MCP |

---

## 4. Workflow

### Branch Naming

```
feature/issue-{number}-short-description
fix/issue-{number}-short-description
chore/issue-{number}-short-description
```

### Your Process

```
1. Read the full issue carefully
2. Identify unknowns → use MCP tools to research
3. Plan your approach
4. Implement iteratively:
   a. Write/update tests
   b. Write implementation
   c. Run validation tools
   d. Fix issues
   e. Repeat until all acceptance criteria pass
5. Self-review your diff
6. Create PR with clear description of what and why
```

---

## 5. Architecture Context

### What We Are Building

A **Label Price Calculator** for a self-adhesive label printing business:
- Customers request quotes for custom labels
- Price depends on: material, dimensions, shape, quantity, printing method,
  number of colors, finishing (lamination, varnish), die-cut complexity
- Integrates with ERPNext's sales flow:
  Quotation → Sales Order → Delivery Note → Sales Invoice

---

## 6. Available MCP Tools Reference

| Tool | What It Does | When to Use |
|---|---|---|
| `github` | Manage issues, PRs, branches | Creating PRs, reading issue details |
| `filesystem` | Read/write files in workspace | Navigating codebase, reading configs |
| `shell` | Execute allowed commands | Tests, linting, bench commands, DB queries |
| `context7` | Library documentation | Frappe Framework + Python lib docs |
| `frappe-mcp` | Frappe instance interaction | Query DocType metadata, read/create documents |

---

*This document is version-controlled. When instructions in a specific issue
conflict with this document, the issue takes precedence for that specific task.*
