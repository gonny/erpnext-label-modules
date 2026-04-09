"""Label price calculator — pure Python calculation engine.

This module contains the core pricing logic with zero Frappe dependencies.
All functions accept plain Python dataclasses or dicts and return the same.
This design ensures fast, isolated unit tests.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class LabelSpec:
    """Specification for a label to be priced.

    All dimensions in millimetres.  Quantity is the number of labels.
    """

    width_mm: float
    height_mm: float
    quantity: int
    material_code: str = "UNKNOWN"


@dataclass
class PriceResult:
    """Result of a label price calculation."""

    unit_price: float
    total_price: float
    currency: str = "CZK"


def calculate_label_price(spec: LabelSpec) -> PriceResult:
    """Calculate the price for a batch of labels.

    This is a **placeholder** implementation.  Real pricing logic will be
    added in a dedicated issue once DocType definitions and material price
    tables exist.

    Args:
        spec: Label specification (dimensions, quantity, material).

    Returns:
        PriceResult with unit and total prices.
    """
    # Placeholder: price = area in cm2 x 0.10 CZK, minimum 1 CZK per label
    area_cm2 = (spec.width_mm / 10) * (spec.height_mm / 10)
    unit_price = max(1.0, round(area_cm2 * 0.10, 4))
    total_price = round(unit_price * spec.quantity, 2)
    return PriceResult(unit_price=unit_price, total_price=total_price)
