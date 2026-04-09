"""Label price calculator — pure Python calculation engine.

This module contains the core pricing logic with zero Frappe dependencies.
All functions accept plain Python dataclasses and return the same.

Two production modes are supported:

- **Thermotransfer (TTR):** Linear consumption — price per cm of ribbon,
  waste baked into per-cm price via division. No pruning waste.

- **Laser:** Area-based — price per mm² of sheet material, waste (test +
  pruning) baked into per-mm² price via division.

In both modes:

- Margin applies ONLY to material cost.
- Labor = global hourly_rate / pieces_per_hour (one formula).
- Unit price rounded UP to 0.10 CZK.
"""

from __future__ import annotations

import math

from label_calculator.core.models import (
    CalcResult,
    JobInput,
    MaterialInput,
    TaxConfig,
    TierInput,
)

# ---------------------------------------------------------------------------
# Tier resolution helpers
# ---------------------------------------------------------------------------


def resolve_tier(
    tiers: list[TierInput],
    quantity: int,
) -> TierInput | None:
    """Find the matching tier for *quantity* by min/max bracket.

    Args:
        tiers: List of tiers filtered by group + profile.
        quantity: Desired label quantity.

    Returns:
        Matching ``TierInput`` or ``None`` if no bracket covers *quantity*.
    """
    for t in tiers:
        if t.min_quantity <= quantity <= t.max_quantity:
            return t
    return None


def resolve_throughput(
    tier: TierInput,
    override_pcs_per_hour: float | None = None,
) -> float:
    """Return effective pieces_per_hour, checking override first."""
    if override_pcs_per_hour is not None and override_pcs_per_hour > 0:
        return override_pcs_per_hour
    return tier.pieces_per_hour


# ---------------------------------------------------------------------------
# Description builder
# ---------------------------------------------------------------------------


def build_description(
    material_name: str,
    addon_color_name: str | None,
    width: float,
    height: float,
    production_type: str,
) -> str:
    """Build a human-readable label description for quotation lines."""
    w = _fmt_mm(width)
    h = _fmt_mm(height)

    if production_type == "thermotransfer" and addon_color_name:
        return f"{material_name} {w}mm × {h}mm, {addon_color_name} tisk"
    return f"{material_name} {w}×{h}mm, {production_type}"


# ---------------------------------------------------------------------------
# Main calculation
# ---------------------------------------------------------------------------


def calculate(
    job: JobInput,
    material: MaterialInput,
    tier: TierInput,
    tax: TaxConfig | None = None,
    hourly_rate: float = 810.0,
    override_pcs_per_hour: float | None = None,
) -> CalcResult:
    """Run the full price calculation.

    Args:
        job: Job specification (dimensions, quantity, production type).
        material: Main material with pricing.
        tier: Active production tier.
        tax: Tax configuration for material gross-up.
        hourly_rate: Global operator rate CZK/hr (default 810).
        override_pcs_per_hour: Material-level throughput override.

    Returns:
        ``CalcResult`` with per-unit cost breakdown.

    Raises:
        ValueError: If dimensions or quantity are zero/negative.
    """
    if job.width <= 0 or job.height <= 0:
        raise ValueError("Label dimensions must be positive")
    if job.quantity <= 0:
        raise ValueError("Quantity must be positive")

    tax = tax or TaxConfig()
    pcs_per_hour = resolve_throughput(tier, override_pcs_per_hour)

    if job.production_type == "thermotransfer":
        return _calc_ttr(job, material, tier, tax, pcs_per_hour, hourly_rate)
    return _calc_laser(job, material, tier, tax, pcs_per_hour, hourly_rate)


# ---------------------------------------------------------------------------
# Laser mode
# ---------------------------------------------------------------------------


def _calc_laser(
    job: JobInput,
    material: MaterialInput,
    tier: TierInput,
    tax: TaxConfig,
    pcs_per_hour: float,
    hourly_rate: float,
) -> CalcResult:
    """Laser: area-based pricing, waste baked into price per mm²."""
    # 1. Price per mm² (waste baked in via division)
    price_incl_vat = material.price_incl_vat
    sheet_area = material.sheet_width * material.sheet_height
    price_per_mm2 = price_incl_vat / ((1 - tier.waste_test_pct / 100) * (1 - tier.waste_pruning_pct / 100) * sheet_area)

    # 2. Material cost per unit
    label_area = job.width * job.height
    material_cost_raw = label_area * price_per_mm2

    # 3. Gross-up (income tax)
    gross_up_divisor = _gross_up_divisor(tax)
    material_cost_raw /= gross_up_divisor

    # 4. Margin on material only
    margin_multiplier = 1 + tier.margin_pct / 100
    material_cost = material_cost_raw * margin_multiplier

    # 5. Labor per unit
    labor_cost = hourly_rate / pcs_per_hour if pcs_per_hour > 0 else 0.0

    # 6. Unit price rounded UP to 0.10 CZK
    unit_price = _round_up_dime(material_cost + labor_cost)
    total_price = unit_price * job.quantity * job.copies

    # Description
    addon_color = material.addons[0].color_name if material.addons else None
    desc = build_description(material.name, addon_color, job.width, job.height, "laser")

    return CalcResult(
        material_cost_raw=material_cost_raw,
        material_cost=material_cost,
        labor_cost=labor_cost,
        unit_price=unit_price,
        total_price=total_price,
        description_line=desc,
        price_per_unit_area=price_per_mm2,
        waste_test_pct=tier.waste_test_pct,
        waste_pruning_pct=tier.waste_pruning_pct,
        gross_up_divisor=gross_up_divisor,
        margin_multiplier=margin_multiplier,
        pieces_per_hour=pcs_per_hour,
    )


# ---------------------------------------------------------------------------
# Thermotransfer mode
# ---------------------------------------------------------------------------


def _calc_ttr(
    job: JobInput,
    material: MaterialInput,
    tier: TierInput,
    tax: TaxConfig,
    pcs_per_hour: float,
    hourly_rate: float,
) -> CalcResult:
    """TTR: linear price per cm, waste baked in, ROUNDUP(..., 3) on per-cm price."""
    # 1. Price per cm for ribbon (waste baked in)
    roll_length_cm = material.roll_length_m * 100
    ribbon_per_cm = _roundup3(material.price_incl_vat / ((1 - tier.waste_test_pct / 100) * roll_length_cm))

    # Addon per cm (e.g. TTR ink ribbon)
    addon_per_cm = 0.0
    for addon in material.addons:
        addon_roll_cm = addon.roll_length_m * 100
        addon_per_cm += _roundup3(addon.price_incl_vat / ((1 - tier.waste_test_pct / 100) * addon_roll_cm))

    # 2. Material cost per unit (label_length in cm)
    label_length_cm = job.height / 10  # mm → cm
    material_cost_raw = label_length_cm * (ribbon_per_cm + addon_per_cm)

    # 3. Gross-up
    gross_up_divisor = _gross_up_divisor(tax)
    material_cost_raw /= gross_up_divisor

    # 4. Margin on material only
    margin_multiplier = 1 + tier.margin_pct / 100
    material_cost = material_cost_raw * margin_multiplier

    # 5. Labor per unit (same formula as laser)
    labor_cost = hourly_rate / pcs_per_hour if pcs_per_hour > 0 else 0.0

    # 6. Unit price rounded UP to 0.10 CZK
    unit_price = _round_up_dime(material_cost + labor_cost)
    total_price = unit_price * job.quantity * job.copies

    # Description
    addon_color = material.addons[0].color_name if material.addons else None
    desc = build_description(material.name, addon_color, job.width, job.height, "thermotransfer")

    return CalcResult(
        material_cost_raw=material_cost_raw,
        material_cost=material_cost,
        labor_cost=labor_cost,
        unit_price=unit_price,
        total_price=total_price,
        description_line=desc,
        price_per_unit_area=ribbon_per_cm + addon_per_cm,
        waste_test_pct=tier.waste_test_pct,
        waste_pruning_pct=0.0,
        gross_up_divisor=gross_up_divisor,
        margin_multiplier=margin_multiplier,
        pieces_per_hour=pcs_per_hour,
    )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _gross_up_divisor(tax: TaxConfig) -> float:
    """Return the divisor for income-tax gross-up."""
    if tax.apply_material_grossup and tax.income_tax_rate > 0:
        return 1 - tax.income_tax_rate / 100
    return 1.0


def _round_up_dime(value: float) -> float:
    """Round UP to nearest 0.10 CZK."""
    return math.ceil(value * 10) / 10


def _roundup3(value: float) -> float:
    """Round UP to 3 decimal places (Excel ROUNDUP behavior)."""
    return math.ceil(value * 1000) / 1000


def _fmt_mm(value: float) -> str:
    """Format mm value without trailing zeros."""
    if value == int(value):
        return str(int(value))
    return f"{value:g}"
