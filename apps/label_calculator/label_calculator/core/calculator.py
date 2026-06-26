"""Label price calculator — pure Python calculation engine.

This module contains the core pricing logic with zero Frappe dependencies.
All functions accept plain Python dataclasses and return the same.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from label_calculator.core.layout import compute_effective_quantity, sheet_layout
from label_calculator.core.machine import round_up
from label_calculator.core.models import (
    AddonInput,
    CalcResult,
    JobInput,
    MachineInput,
    MaterialInput,
    MaterialMachineParams,
    TierInput,
)

# Default description label used when no addon is explicitly selected.
DEFAULT_ADDON_NAME = "standard"


@dataclass(frozen=True)
class LabelSpec:
    """Specification for a label to be priced.

    All dimensions are in millimeters. Quantity is the number of labels.
    """

    width_mm: float
    height_mm: float
    quantity: int
    material_code: str = "UNKNOWN"
    production_type: str = "laser"
    price_ex_vat: float = 1.0
    vat_rate: float = 21.0
    hourly_rate: float = 20.0
    pieces_per_hour: float = 100.0
    margin_pct: float = 0.0
    waste_test_pieces: int = 0
    waste_test_pct: float = 0.0
    waste_pruning_pct: float = 0.0
    sheet_width_mm: float = 100.0
    sheet_height_mm: float = 100.0
    material_type: str = "sheet"
    cut_margin_pct: float = 0.0


@dataclass(frozen=True)
class PriceResult:
    """Result of a label price calculation."""

    unit_price: float
    total_price: float
    currency: str = "CZK"


def calculate_label_price(spec: LabelSpec) -> PriceResult:
    """Calculate the price for a batch of labels."""
    if spec.width_mm <= 0 or spec.height_mm <= 0:
        raise ValueError("Dimensions must be positive")
    if spec.quantity <= 0:
        raise ValueError("Quantity must be positive")

    material = MaterialInput(
        name=spec.material_code,
        price_ex_vat=spec.price_ex_vat,
        sheet_width=spec.sheet_width_mm,
        sheet_height=spec.sheet_height_mm,
        material_type=spec.material_type,
        cut_margin_pct=spec.cut_margin_pct,
        vat_rate=spec.vat_rate,
    )
    machine = MachineInput(hourly_rate=spec.hourly_rate)
    tier = TierInput(
        pieces_per_hour=spec.pieces_per_hour,
        margin_pct=spec.margin_pct,
        waste_test_pieces=spec.waste_test_pieces,
        waste_test_pct=spec.waste_test_pct,
        waste_pruning_pct=spec.waste_pruning_pct,
    )
    params = MaterialMachineParams()
    job = JobInput(
        width=spec.width_mm,
        height=spec.height_mm,
        quantity=spec.quantity,
        production_type=spec.production_type,
    )

    result = calculate_pricing(material, machine, params, tier, job)
    return PriceResult(unit_price=result.unit_price, total_price=result.total_price)


def calculate_pricing(
    material: MaterialInput,
    machine: MachineInput,
    params: MaterialMachineParams,
    tier: TierInput,
    job: JobInput,
    income_tax_rate: float = 15.0,
    apply_material_grossup: bool = True,
) -> CalcResult:
    """Calculate a full pricing breakdown for the supplied job."""
    if job.production_type not in {"laser", "thermotransfer"}:
        raise ValueError("Unsupported production type")

    if job.width <= 0 or job.height <= 0:
        raise ValueError("Dimensions must be positive")
    if job.quantity <= 0:
        raise ValueError("Quantity must be positive")

    effective_quantity = compute_effective_quantity(job.quantity, tier)

    material_cost_raw = 0.0
    addon_cost_raw = 0.0
    labels_per_sheet = 1
    sheets_needed = 1

    if job.production_type == "thermotransfer":
        ribbon_length_m = job.height / 1000.0
        material_cost_raw = ribbon_length_m * material.price_incl_vat * effective_quantity
        addon_cost_raw = sum(ribbon_length_m * addon.price_incl_vat * effective_quantity for addon in material.addons)
    else:
        labels_per_sheet = sheet_layout(
            material.sheet_width,
            material.sheet_height,
            job.width,
            job.height,
        )
        sheets_needed = math.ceil(effective_quantity / labels_per_sheet)
        material_cost_raw = sheets_needed * material.price_incl_vat

    material_cost = material_cost_raw + addon_cost_raw
    if apply_material_grossup:
        if income_tax_rate < 0:
            raise ValueError("income_tax_rate must be non-negative")
        if income_tax_rate >= 100:
            raise ValueError("income_tax_rate must be less than 100")
        material_cost = material_cost / (1 - (income_tax_rate / 100))

    labor_cost = machine.hourly_rate / tier.pieces_per_hour * effective_quantity
    margin_amount = material_cost * (tier.margin_pct / 100)
    base_total = material_cost + labor_cost + margin_amount
    step = 0.001 if job.production_type == "thermotransfer" else 0.10
    unit_price = max(1.0, round_up(base_total / job.quantity, step))
    total_price = round_up(unit_price * job.quantity, step)

    # Use the first addon in the description so laser/TTR quotes remain readable.
    first_addon = material.addons[0] if material.addons else None
    description_line = build_description(
        material,
        first_addon,
        job.width,
        job.height,
        job.production_type,
    )
    return CalcResult(
        material_cost_raw=material_cost_raw,
        material_cost=material_cost,
        labor_cost=labor_cost,
        unit_price=unit_price,
        total_price=total_price,
        description_line=description_line,
        labels_per_sheet=labels_per_sheet,
        sheets_needed=sheets_needed,
    )


def build_description(
    material: MaterialInput,
    addon: AddonInput | None,
    width: float,
    height: float,
    production_type: str,
) -> str:
    """Create a human-readable description for the calculated label."""
    addon_name = addon.name if addon else DEFAULT_ADDON_NAME
    if production_type == "thermotransfer":
        return f"{material.name} {int(width)}mm x {int(height)}mm, {addon_name} tisk"
    return f"{material.name} {int(width)}mm x {int(height)}mm, laser"
