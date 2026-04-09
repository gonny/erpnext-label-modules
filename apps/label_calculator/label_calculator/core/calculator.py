"""Label price calculator — pure Python calculation engine.

This module contains the core pricing logic with zero Frappe dependencies.
All functions accept plain Python dataclasses and return the same.
This design ensures fast, isolated unit tests.

Two production modes are supported:

- **Thermotransfer (TTR):** Linear consumption (length × price). Addon
  (ribbon) consumed alongside. Kerf = 0. Waste = test pieces only (no pruning).
  Machine + operator counted ONCE (single pass).

- **Laser:** Area-based consumption (sheet nesting). Kerf reduces usable
  area. Waste = test pieces + test% + pruning%. Machine + operator counted
  from tier pieces_per_hour.
"""

from __future__ import annotations

import math

from label_calculator.core.layout import compute_effective_quantity, sheet_layout
from label_calculator.core.models import (
    CalcResult,
    JobInput,
    MachineInput,
    MaterialInput,
    MaterialMachineParams,
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
    """Find the matching tier for *quantity*.

    Args:
        tiers: List of tiers (already filtered by group + profile).
        quantity: Desired label quantity.

    Returns:
        Matching ``TierInput`` or ``None`` if no bracket covers *quantity*.
    """
    for t in tiers:
        # Tiers don't carry min/max themselves — the caller pre-filters.
        # When called from DocType layer, tiers are already the correct list.
        return t  # first element = correct tier (pre-filtered)
    return None


def resolve_throughput(
    tier: TierInput,
    override_pcs_per_hour: float | None = None,
) -> float:
    """Return effective pieces_per_hour, checking override first.

    Args:
        tier: The tier supplying the default throughput.
        override_pcs_per_hour: Material-specific override (or ``None``).

    Returns:
        Effective throughput in pieces per hour.
    """
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
    """Build a human-readable label description for quotation lines.

    Examples:
        - TTR: ``"Saténová stuha 25mm × 80mm, stříbrný tisk"``
        - Laser: ``"Bílý vinyl 50×30mm, laser"``

    Args:
        material_name: Display name of the main material.
        addon_color_name: Colour of the addon ribbon (TTR only).
        width: Label width in mm.
        height: Label height/length in mm.
        production_type: ``"thermotransfer"`` or ``"laser"``.

    Returns:
        Description string.
    """
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
    machine: MachineInput,
    params: MaterialMachineParams,
    tier: TierInput,
    tax: TaxConfig | None = None,
    override_pcs_per_hour: float | None = None,
) -> CalcResult:
    """Run the full price calculation.

    Args:
        job: Job specification (dimensions, quantity, production type).
        material: Main material properties.
        machine: Machine with hourly rate.
        params: Material × machine combination parameters.
        tier: Active production tier.
        tax: Tax configuration for material gross-up (optional).
        override_pcs_per_hour: Material-level throughput override.

    Returns:
        ``CalcResult`` with full cost breakdown.

    Raises:
        ValueError: If dimensions are zero/negative.
    """
    if job.width <= 0 or job.height <= 0:
        raise ValueError("Label dimensions must be positive")
    if job.quantity <= 0:
        raise ValueError("Quantity must be positive")

    tax = tax or TaxConfig()
    pcs_per_hour = resolve_throughput(tier, override_pcs_per_hour)

    if job.production_type == "thermotransfer":
        return _calc_ttr(job, material, machine, params, tier, tax, pcs_per_hour)
    return _calc_laser(job, material, machine, params, tier, tax, pcs_per_hour)


# ---------------------------------------------------------------------------
# Laser mode
# ---------------------------------------------------------------------------


def _calc_laser(
    job: JobInput,
    material: MaterialInput,
    machine: MachineInput,
    params: MaterialMachineParams,
    tier: TierInput,
    tax: TaxConfig,
    pcs_per_hour: float,
) -> CalcResult:
    """Laser calculation: area-based sheet nesting, kerf, full waste."""
    kerf = params.kerf_mm

    # Layout
    lps = sheet_layout(material.sheet_width, material.sheet_height, job.width, job.height, kerf)

    # Effective quantity including waste
    eff_qty = compute_effective_quantity(job.quantity * job.copies, tier)

    sheets = math.ceil(eff_qty / lps) if lps > 0 else eff_qty

    # Material cost: sheets × price_per_unit
    raw_material_cost = sheets * material.price_per_unit

    # Addon cost (laser mode rarely has addons, but support it)
    raw_addon_cost = 0.0
    for addon in material.addons:
        raw_addon_cost += sheets * addon.price_per_unit

    # Apply gross-up to material & addon costs
    material_cost = _apply_grossup(raw_material_cost, tax)
    addon_cost = _apply_grossup(raw_addon_cost, tax)

    # Machine cost: time based on throughput
    total_pieces = job.quantity * job.copies
    production_hours = total_pieces / pcs_per_hour if pcs_per_hour > 0 else 0
    machine_cost = production_hours * machine.hourly_rate

    # Operator cost
    setup_hours = job.setup_time_min / 60
    if job.operator_time_per_unit_sec > 0:
        operator_production_hours = total_pieces * job.operator_time_per_unit_sec / 3600
    else:
        operator_production_hours = production_hours
    operator_cost = (setup_hours + operator_production_hours) * job.operator_rate

    # Waste cost = (effective - actual) / effective × material_cost
    actual_qty = job.quantity * job.copies
    waste_ratio = (eff_qty - actual_qty) / eff_qty if eff_qty > 0 else 0
    waste_cost = waste_ratio * material_cost

    # Subtotal
    subtotal = material_cost + addon_cost + machine_cost + operator_cost

    # Margin
    margin_amount = subtotal * tier.margin_pct / 100

    # Total and unit price
    total_price = subtotal + margin_amount
    unit_price = total_price / actual_qty if actual_qty > 0 else 0

    # Description
    addon_color = material.addons[0].color_name if material.addons else None
    desc = build_description(material.name, addon_color, job.width, job.height, "laser")

    return CalcResult(
        labels_per_sheet=lps,
        sheets_needed=sheets,
        material_cost=round(material_cost, 4),
        addon_cost=round(addon_cost, 4),
        machine_cost=round(machine_cost, 4),
        operator_cost=round(operator_cost, 4),
        waste_cost=round(waste_cost, 4),
        subtotal=round(subtotal, 4),
        margin_amount=round(margin_amount, 4),
        total_price=round(total_price, 4),
        unit_price=round(unit_price, 4),
        description_line=desc,
    )


# ---------------------------------------------------------------------------
# Thermotransfer mode
# ---------------------------------------------------------------------------


def _calc_ttr(
    job: JobInput,
    material: MaterialInput,
    machine: MachineInput,
    params: MaterialMachineParams,
    tier: TierInput,
    tax: TaxConfig,
    pcs_per_hour: float,
) -> CalcResult:
    """Thermotransfer calculation: linear consumption, single pass."""
    total_pieces = job.quantity * job.copies

    # TTR waste: test pieces only, no pruning
    ttr_tier = TierInput(
        pieces_per_hour=tier.pieces_per_hour,
        margin_pct=tier.margin_pct,
        waste_test_pieces=tier.waste_test_pieces,
        waste_test_pct=tier.waste_test_pct,
        waste_pruning_pct=0.0,  # No pruning in TTR
    )
    eff_qty = compute_effective_quantity(total_pieces, ttr_tier)

    # For TTR/rolls, labels_per_sheet = how many labels per roll segment
    # But typically it's 1 label = 1 length unit, so we use linear consumption.
    # Material consumption: length per label × effective quantity × price/mm
    label_length_mm = job.height  # height = length for TTR
    total_length_mm = label_length_mm * eff_qty

    # Price per mm = price_per_unit / sheet_height (roll_length in mm)
    price_per_mm = material.price_per_unit / material.sheet_height if material.sheet_height > 0 else 0
    raw_material_cost = total_length_mm * price_per_mm

    # Addon (ribbon) — same length consumption
    raw_addon_cost = 0.0
    for addon in material.addons:
        addon_price_per_mm = addon.price_per_unit / material.sheet_height if material.sheet_height > 0 else 0
        raw_addon_cost += total_length_mm * addon_price_per_mm

    # Apply gross-up
    material_cost = _apply_grossup(raw_material_cost, tax)
    addon_cost = _apply_grossup(raw_addon_cost, tax)

    # Machine + operator counted ONCE (single pass, addon does NOT add time)
    production_hours = total_pieces / pcs_per_hour if pcs_per_hour > 0 else 0
    machine_cost = production_hours * machine.hourly_rate

    setup_hours = job.setup_time_min / 60
    if job.operator_time_per_unit_sec > 0:
        operator_production_hours = total_pieces * job.operator_time_per_unit_sec / 3600
    else:
        operator_production_hours = production_hours
    operator_cost = (setup_hours + operator_production_hours) * job.operator_rate

    # Waste cost
    waste_ratio = (eff_qty - total_pieces) / eff_qty if eff_qty > 0 else 0
    waste_cost = waste_ratio * material_cost

    # Labels per sheet for TTR = effectively linear (1 per unit of length)
    labels_per_sheet = 1
    sheets_needed = eff_qty  # each "sheet" = one label length on the roll

    # Subtotal
    subtotal = material_cost + addon_cost + machine_cost + operator_cost

    # Margin
    margin_amount = subtotal * tier.margin_pct / 100

    # Total
    total_price = subtotal + margin_amount
    unit_price = total_price / total_pieces if total_pieces > 0 else 0

    # Description
    addon_color = material.addons[0].color_name if material.addons else None
    desc = build_description(material.name, addon_color, job.width, job.height, "thermotransfer")

    return CalcResult(
        labels_per_sheet=labels_per_sheet,
        sheets_needed=sheets_needed,
        material_cost=round(material_cost, 4),
        addon_cost=round(addon_cost, 4),
        machine_cost=round(machine_cost, 4),
        operator_cost=round(operator_cost, 4),
        waste_cost=round(waste_cost, 4),
        subtotal=round(subtotal, 4),
        margin_amount=round(margin_amount, 4),
        total_price=round(total_price, 4),
        unit_price=round(unit_price, 4),
        description_line=desc,
    )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _apply_grossup(cost: float, tax: TaxConfig) -> float:
    """Apply income-tax gross-up to material/addon cost.

    Divides by ``(1 - tax_rate/100)`` when enabled.
    """
    if not tax.apply_material_grossup or tax.income_tax_rate <= 0:
        return cost
    return cost / (1 - tax.income_tax_rate / 100)


def _fmt_mm(value: float) -> str:
    """Format mm value without trailing zeros."""
    if value == int(value):
        return str(int(value))
    return f"{value:g}"
