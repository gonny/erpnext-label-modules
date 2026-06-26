"""Core data models used by the pure-Python pricing engine."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class AddonInput:
    """A consumable addon used alongside the main material."""

    name: str
    price_ex_vat: float
    sheet_width: float
    vat_rate: float = 0.21

    @property
    def price_incl_vat(self) -> float:
        """Return the VAT-inclusive purchase price for this addon."""
        return self.price_ex_vat * (1 + self.vat_rate / 100)


@dataclass(frozen=True)
class MaterialInput:
    """A material that can be used in laser or thermotransfer pricing."""

    name: str
    price_ex_vat: float
    sheet_width: float
    sheet_height: float
    material_type: str = "sheet"
    cut_margin_pct: float = 0.0
    vat_rate: float = 0.21
    addons: tuple[AddonInput, ...] = field(default_factory=tuple)

    @property
    def price_incl_vat(self) -> float:
        """Return the VAT-inclusive purchase price for this material."""
        return self.price_ex_vat * (1 + self.vat_rate / 100)


@dataclass(frozen=True)
class MachineInput:
    """A production machine with an hourly cost rate."""

    hourly_rate: float


@dataclass(frozen=True)
class MaterialMachineParams:
    """Material/machine parameters used by the laser layout logic."""

    cut_speed_mm_per_sec: float
    kerf_mm: float


@dataclass(frozen=True)
class TierInput:
    """Production tier for a material group and pricing profile."""

    pieces_per_hour: float
    margin_pct: float
    waste_test_pieces: int = 0
    waste_test_pct: float = 0.0
    waste_pruning_pct: float = 0.0
    min_quantity: int = 1
    max_quantity: int = 999999


@dataclass(frozen=True)
class JobInput:
    """The order/job description passed to the pricing engine."""

    width: float
    height: float
    quantity: int
    copies: int = 1
    production_type: str = "laser"


@dataclass(frozen=True)
class CalcResult:
    """The pricing breakdown returned by the core engine."""

    material_cost_raw: float
    material_cost: float
    labor_cost: float
    unit_price: float
    total_price: float
    description_line: str
    labels_per_sheet: int = 1
    sheets_needed: int = 1
