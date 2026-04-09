"""Tests for description builder."""

import pytest

from label_calculator.core.calculator import build_description


@pytest.mark.unit
def test_ttr_description() -> None:
    """TTR description: 'Saténová stuha 25mm × 80mm, stříbrný tisk'."""
    desc = build_description(
        material_name="Saténová stuha",
        addon_color_name="stříbrný",
        width=25.0,
        height=80.0,
        production_type="thermotransfer",
    )
    assert desc == "Saténová stuha 25mm × 80mm, stříbrný tisk"


@pytest.mark.unit
def test_laser_description() -> None:
    """Laser description: 'Bílý vinyl 50×30mm, laser'."""
    desc = build_description(
        material_name="Bílý vinyl",
        addon_color_name=None,
        width=50.0,
        height=30.0,
        production_type="laser",
    )
    assert desc == "Bílý vinyl 50×30mm, laser"


@pytest.mark.unit
def test_ttr_description_no_addon() -> None:
    """TTR without addon falls back to production type in description."""
    desc = build_description(
        material_name="Saténová stuha",
        addon_color_name=None,
        width=25.0,
        height=80.0,
        production_type="thermotransfer",
    )
    assert desc == "Saténová stuha 25×80mm, thermotransfer"
