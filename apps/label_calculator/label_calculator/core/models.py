"""Pure Python dataclasses for the label price calculation engine.

These models define the input/output contracts for the calculator.
ZERO Frappe imports — testable in isolation.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class AddonInput:
    """An addon material consumed alongside the main material (e.g. TTR ribbon)."""

    purchase_price: float
    purchase_vat_included: bool = True
    purchase_vat_pct: float = 21.0
    roll_width_mm: float = 0.0
    roll_length_m: float = 200.0
    color_name: str = ""

    @property
    def price_incl_vat(self) -> float:
        """Purchase price always including VAT (non-VAT-payer cost)."""
        if self.purchase_vat_included:
            return self.purchase_price
        return self.purchase_price * (1 + self.purchase_vat_pct / 100)


@dataclass(frozen=True)
class MaterialInput:
    """A specific material with pricing and dimensions."""

    purchase_price: float
    purchase_vat_included: bool = True
    purchase_vat_pct: float = 21.0
    sheet_width: float = 0.0
    sheet_height: float = 0.0
    roll_width_mm: float = 0.0
    roll_length_m: float = 0.0
    material_type: str = "sheet"  # "sheet" or "roll"
    name: str = ""
    addons: list[AddonInput] = field(default_factory=list)

    @property
    def price_incl_vat(self) -> float:
        """Purchase price always including VAT (non-VAT-payer cost)."""
        if self.purchase_vat_included:
            return self.purchase_price
        return self.purchase_price * (1 + self.purchase_vat_pct / 100)


@dataclass(frozen=True)
class MachineInput:
    """Machine with computed hourly rate.

    Used by the DocType layer for amortization calculation.
    NOT used by the pricing calculator (hourly_rate is a global parameter).
    """

    hourly_rate: float


@dataclass(frozen=True)
class MaterialMachineParams:
    """Per-combination parameters for material × machine.

    Used by the DocType layer for cut-speed and kerf storage.
    NOT used by the pricing calculator.
    """

    cut_speed_mm_per_sec: float
    kerf_mm: float


@dataclass(frozen=True)
class TierInput:
    """Production tier with quantity bracket parameters."""

    pieces_per_hour: float
    margin_pct: float
    waste_test_pct: float = 10.0
    waste_pruning_pct: float = 10.0
    waste_test_pieces: int = 0
    min_quantity: int = 0
    max_quantity: int = 999_999


@dataclass(frozen=True)
class JobInput:
    """Job specification for a label calculation."""

    width: float  # mm
    height: float  # mm
    quantity: int
    copies: int = 1
    production_type: str = "laser"  # "thermotransfer" | "laser"


@dataclass(frozen=True)
class TaxConfig:
    """Global tax/grossup configuration."""

    income_tax_rate: float = 15.0
    apply_material_grossup: bool = True


@dataclass
class CalcResult:
    """Full result of a label price calculation."""

    material_cost_raw: float  # per unit, before margin
    material_cost: float  # per unit, with margin
    labor_cost: float  # per unit (hourly_rate / pcs_per_hour)
    unit_price: float  # material_cost + labor, rounded ↑ 0.10
    total_price: float  # unit_price × quantity
    description_line: str = ""

    # Diagnostic / breakdown:
    price_per_unit_area: float = 0.0
    waste_test_pct: float = 0.0
    waste_pruning_pct: float = 0.0
    gross_up_divisor: float = 1.0
    margin_multiplier: float = 1.0
    pieces_per_hour: float = 0.0
