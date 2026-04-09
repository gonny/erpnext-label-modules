"""Pure Python dataclasses for the label price calculation engine.

These models define the input/output contracts for the calculator.
ZERO Frappe imports — testable in isolation.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class MaterialInput:
    """A specific material with pricing and dimensions."""

    price_per_unit: float
    sheet_width: float
    sheet_height: float
    material_type: str  # "Sheet" or "Roll"
    cut_margin_pct: float = 0.0
    name: str = ""
    color_name: str = ""
    addons: list[AddonInput] = field(default_factory=list)


@dataclass(frozen=True)
class AddonInput:
    """An addon material consumed alongside the main material (e.g. TTR ribbon)."""

    price_per_unit: float
    sheet_width: float  # ribbon width — auto-fills label width for TTR
    name: str = ""
    color_name: str = ""


@dataclass(frozen=True)
class MachineInput:
    """Machine with computed hourly rate."""

    hourly_rate: float


@dataclass(frozen=True)
class MaterialMachineParams:
    """Per-combination parameters for material x machine."""

    cut_speed_mm_per_sec: float
    kerf_mm: float


@dataclass(frozen=True)
class TierInput:
    """Production tier with quantity bracket parameters."""

    pieces_per_hour: float
    margin_pct: float
    waste_test_pieces: int = 0
    waste_test_pct: float = 10.0
    waste_pruning_pct: float = 10.0


@dataclass(frozen=True)
class JobInput:
    """Job specification for a label calculation."""

    width: float  # mm
    height: float  # mm
    quantity: int
    copies: int = 1
    production_type: str = "laser"  # "thermotransfer" | "laser"
    operator_rate: float = 0.0  # CZK per hour
    setup_time_min: float = 0.0
    operator_time_per_unit_sec: float = 0.0


@dataclass(frozen=True)
class TaxConfig:
    """Global tax/grossup configuration."""

    income_tax_rate: float = 15.0
    apply_material_grossup: bool = True


@dataclass
class CalcResult:
    """Full result of a label price calculation."""

    labels_per_sheet: int
    sheets_needed: int
    material_cost: float
    addon_cost: float
    machine_cost: float
    operator_cost: float
    waste_cost: float
    subtotal: float
    margin_amount: float
    total_price: float
    unit_price: float
    description_line: str = ""


# Fix forward reference — AddonInput is used before its definition in MaterialInput
# Python 3.11+ with `from __future__ import annotations` resolves this at runtime.
