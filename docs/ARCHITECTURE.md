# Architecture

## Overview

Label Calculator is a **custom Frappe/ERPNext v16 app** that computes prices
for self-adhesive labels. It integrates into the ERPNext sales workflow:

```
Quotation → Sales Order → Delivery Note → Sales Invoice
```

## Layer Diagram

```
┌─────────────────────────────────────────────────────────────┐
│  ERPNext Desk (Frappe v16 native UI — Tailwind, dark mode)  │
└───────────────────────────────┬─────────────────────────────┘
                                │ @frappe.whitelist() REST API
                                ▼
┌───────────────────────────────────────────────────────────┐
│  api/          Whitelisted API methods (thin wrappers)    │
└───────────────────────────────┬───────────────────────────┘
                                │ calls
                                ▼
┌───────────────────────────────────────────────────────────┐
│  core/         Pure Python calculation engine             │
│                - calculator.py   (label pricing)          │
│                - No Frappe imports — unit-testable        │
└───────────────────────────────────────────────────────────┘
                                │ called from
                                ▲
┌───────────────────────────────────────────────────────────┐
│  label_calculator/doctype/    Frappe DocType controllers  │
│  (thin adapters — call core/, save results to doc fields) │
└───────────────────────────────────────────────────────────┘
```

## Module Layout

```
apps/label_calculator/label_calculator/
├── __init__.py          # app version
├── hooks.py             # Frappe app hooks
├── patches/             # Schema migration patches
├── label_calculator/    # Frappe module sub-package
│   ├── doctype/         # DocType JSON + Python controllers
│   └── __init__.py
├── api/                 # @frappe.whitelist() REST endpoints
│   └── __init__.py
├── core/                # Pure Python engine (no Frappe)
│   ├── __init__.py
│   └── calculator.py
├── tests/               # pytest unit + integration tests
│   ├── conftest.py
│   └── test_placeholder.py
└── templates/           # Jinja print-format templates
```

## Testing Strategy

| Level | Marker | What it tests | Requires |
|---|---|---|---|
| Unit | `@pytest.mark.unit` | `core/` functions | Nothing (plain Python) |
| Integration | `@pytest.mark.integration` | DocTypes, API, workflows | Running Frappe + MariaDB |
| Slow | `@pytest.mark.slow` | Heavy/long-running tests | Running Frappe + MariaDB |

## Technology Stack

| Layer | Technology | Version |
|---|---|---|
| Framework | Frappe Framework | v16 (version-16 branch) |
| ERP | ERPNext CE | v16 (version-16 branch) |
| Database | MariaDB | 10.8+ |
| Cache | Redis | Alpine |
| Language | Python | 3.11+ |
| Runtime | Node.js | 20+ |
| Testing | pytest + Frappe test runner | native |
| CI/CD | GitHub Actions | — |
| Containerization | Docker + DevContainers | — |

## Key Design Decisions

1. **Calculation engine is framework-agnostic** — `core/` is pure Python so
   unit tests run without a Frappe instance (fast, CI-friendly).
2. **ERPNext is not modified** — all customization is in our custom app.
3. **API-first** — every calculation is accessible via a REST endpoint.
4. **Czech locale** — currency is CZK, rounding follows Czech rules.
5. **Progressive complexity** — features are added via dedicated GitHub
   issues; each issue leaves the codebase in a releasable state.
