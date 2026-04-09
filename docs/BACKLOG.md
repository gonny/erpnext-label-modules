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

---

## 3. DocType Schema Updates for New Calculator Formulas

**Priority:** High — needed for DocType ↔ engine integration.

The calculation engine was refactored to use new formulas (division-based
waste, per-unit pricing, VAT-inclusive material prices). The DocType schemas
need corresponding updates:

- **Label Calculator Settings:** Add `hourly_rate` (Currency, default 810)
  as the global operator rate parameter.
- **Label Material:** Add `purchase_vat_included` (Check) and
  `purchase_vat_pct` (Float, default 21) fields. Add `roll_width_mm`
  and `roll_length_m` for roll-type materials.
- **Label Material Addon (child):** Add the same VAT and roll fields.

**Trigger:** Next development sprint after engine stabilization.

---

## 4. Machine Amortization as Separate Cost Line

**Description:** Add optional per-unit machine amortization cost to the
calculator output. The `Label Machine` DocType already stores
purchase_price and lifetime_hours. The `machine.py` module already
computes hourly rate. This needs to be wired into the calculator as
an optional component (toggled in Label Calculator Settings).

**Trigger:** Create issue when amortization pricing is needed in quotes.

---

## 5. Admin Overhead Toggle

**Description:** Optional per-order admin overhead (configurable minutes
at the global hourly rate). Odoo implementation had this as a toggle in
system parameters. Adds a flat per-order cost divided by quantity.

---

## 6. Customer Discount Tiers (Bronze/Silver/Gold)

**Description:** Automatic discount tier assignment based on cumulative
customer spending. Manual override support. Discount applied on SO lines
and propagated to invoices. Odoo tests 17-22 cover this functionality.

---

## 7. Czech Payment Infrastructure

**Description:** Variable symbol generation, SPD string, QR/EPC payment
codes, bank account auto-selection by currency, cash rounding. Odoo
tests 23-31 cover this functionality. Specific to Czech accounting.

---

## 8. Multi-Currency Price Conversion

**Description:** Currency conversion on SO lines, price recalculation
on currency change, "Update Prices" regression protection. Odoo tests
32-34 cover this functionality.

---

## 9. VIP Pricing Profiles

**Description:** VIP customers get separate tier brackets with different
margins. VIP eligibility computation, fallback to standard tiers, no
discount for VIP profile. Odoo tests 35-40 cover this functionality.

---

## 10. Combined Production Types

**Description:** Labels requiring multiple production steps (e.g.
print → laser → heat press). Each step has its own material/machine
cost. Not in current engine scope.
