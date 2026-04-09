# Backlog — Future Items (Out of Scope)

This document tracks features that are recognized future needs but are
**explicitly NOT in scope** for current development. Do not implement or
prepare for these items unless a dedicated issue is created.

---

## 1. Public-Facing Calculator Website

**Description:** A customer-facing label price estimator website where
visitors can configure their label parameters and receive an instant quote.

**Technology stack (planned):**
- Astro 6 with Svelte islands
- Hosted on Cloudflare Pages
- Separate repository (not this one)
- Consumes ERPNext REST API for pricing

**Why deferred:** The calculation engine and ERPNext integration must be
stable before building a public UI. The frontend architecture decisions
(Astro + Svelte) are already defined but depend on a working API layer.

**Trigger:** Create a dedicated issue once the core calculation engine
(ERPNext API) is production-ready and documented.

---

## 2. Contact / Customer Import from Profit (Firebird DB)

**Description:** Migration of existing invoicing data from the legacy
Profit accounting system (Firebird database) into ERPNext:
- Customers and contacts
- Historical invoices
- Existing price agreements

**Why deferred:** ERPNext must be fully set up and stable before importing
historical data. A migration error would corrupt production data.
The Profit system remains in parallel use until ERPNext is validated.

**Trigger:** Create a dedicated issue once ERPNext is in production use
and the data model is stable.

---

*Items are added here when recognized during planning and moved to a
dedicated issue when implementation begins.*
