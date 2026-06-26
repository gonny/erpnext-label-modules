"""Machine cost helpers for the pure-Python pricing engine."""

from __future__ import annotations

import math


def compute_hourly_rate(
    purchase_price: float,
    lifetime_hours: float,
    maintenance_annual: float,
    energy_cost_per_hr: float,
    working_hours_per_year: float = 2000.0,
) -> float:
    """Return a machine hourly rate from amortization and operating costs."""
    if lifetime_hours <= 0:
        raise ValueError("lifetime_hours must be positive")

    depreciation = purchase_price / lifetime_hours
    maintenance = maintenance_annual / working_hours_per_year
    return depreciation + maintenance + energy_cost_per_hr


def round_up(value: float, step: float = 0.10) -> float:
    """Round a number up to the nearest step."""
    if step <= 0:
        raise ValueError("step must be positive")
    return math.ceil(value / step) * step
