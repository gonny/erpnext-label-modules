"""Tests for core/layout.py — sheet nesting and waste computation."""

import pytest

from label_calculator.core.layout import (
    compute_effective_quantity,
    roll_layout,
    sheet_layout,
)
from label_calculator.core.models import TierInput


@pytest.mark.unit
def test_sheet_layout_basic() -> None:
    """305×610 sheet, 50×30 labels, no kerf → 6×20 = 120."""
    count = sheet_layout(305, 610, 50, 30, kerf=0)
    # 305/50=6, 610/30=20 → 120
    assert count == 120


@pytest.mark.unit
def test_sheet_layout_with_kerf_reduces_count() -> None:
    """Kerf reduces the number of labels per sheet."""
    without_kerf = sheet_layout(305, 610, 50, 30, kerf=0)
    with_kerf = sheet_layout(305, 610, 50, 30, kerf=0.15)
    assert with_kerf <= without_kerf


@pytest.mark.unit
def test_sheet_layout_rotation() -> None:
    """Try both orientations and pick the best one."""
    # 210×297 sheet, 100×40 labels → orientation A: 2×7=14, orientation B: 5×2=10 → 14
    count = sheet_layout(210, 297, 100, 40, kerf=0)
    assert count == 14


@pytest.mark.unit
def test_sheet_layout_minimum_one() -> None:
    """Even if label barely fits, return at least 1."""
    count = sheet_layout(50, 50, 60, 60, kerf=0)
    assert count >= 1


@pytest.mark.unit
def test_sheet_layout_zero_dimensions_raises() -> None:
    """Zero label dimensions should raise ValueError."""
    with pytest.raises(ValueError):
        sheet_layout(305, 610, 0, 30, kerf=0)


@pytest.mark.unit
def test_roll_layout() -> None:
    """Roll 25mm wide × 100m, labels 25×80mm → 25/25=1 across, 100000/80=1250 down."""
    count = roll_layout(25, 100_000, 25, 80, kerf=0)
    assert count == 1250


@pytest.mark.unit
def test_effective_quantity_all_waste_components() -> None:
    """100 pcs + 5 test + ceil(100*15%) + ceil(100*12%) = 100+5+15+12 = 132."""
    tier = TierInput(
        pieces_per_hour=150,
        margin_pct=50,
        waste_test_pieces=5,
        waste_test_pct=15.0,
        waste_pruning_pct=12.0,
    )
    eff = compute_effective_quantity(100, tier)
    assert eff == 132


@pytest.mark.unit
def test_effective_quantity_no_waste() -> None:
    """With zero waste params, effective equals input quantity."""
    tier = TierInput(
        pieces_per_hour=800,
        margin_pct=25,
        waste_test_pieces=0,
        waste_test_pct=0.0,
        waste_pruning_pct=0.0,
    )
    eff = compute_effective_quantity(100, tier)
    assert eff == 100
