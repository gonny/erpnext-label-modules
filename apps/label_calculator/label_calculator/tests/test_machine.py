"""Tests for core/machine.py — machine hourly rate computation."""

import pytest

from label_calculator.core.machine import compute_hourly_rate


@pytest.mark.unit
def test_hourly_rate_known_values() -> None:
    """Epilog Laser: 400k/15000h + 15k/2000h + 8 = 26.667 + 7.5 + 8 = 42.167."""
    rate = compute_hourly_rate(
        purchase_price=400_000,
        lifetime_hrs=15_000,
        maintenance_annual=15_000,
        energy_cost_per_hr=8.0,
        working_hrs_per_year=2000,
    )
    assert abs(rate - 42.1667) < 0.01


@pytest.mark.unit
def test_hourly_rate_ttr_printer() -> None:
    """TTR Printer: 80k/10000h + 5k/2000h + 3 = 8 + 2.5 + 3 = 13.5."""
    rate = compute_hourly_rate(
        purchase_price=80_000,
        lifetime_hrs=10_000,
        maintenance_annual=5_000,
        energy_cost_per_hr=3.0,
        working_hrs_per_year=2000,
    )
    assert abs(rate - 13.5) < 0.01


@pytest.mark.unit
def test_zero_lifetime_raises() -> None:
    """Zero lifetime hours should raise ValueError."""
    with pytest.raises(ValueError, match="positive"):
        compute_hourly_rate(
            purchase_price=100_000,
            lifetime_hrs=0,
            maintenance_annual=5000,
            energy_cost_per_hr=5.0,
        )
