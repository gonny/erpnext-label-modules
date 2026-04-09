"""Machine hourly rate computation — pure Python, zero Frappe imports."""

from __future__ import annotations


def compute_hourly_rate(
    purchase_price: float,
    lifetime_hrs: float,
    maintenance_annual: float,
    energy_cost_per_hr: float,
    working_hrs_per_year: float = 2000.0,
) -> float:
    """Compute machine hourly rate from amortization parameters.

    Formula: depreciation_per_hr + maintenance_per_hr + energy_per_hr

    Args:
        purchase_price: Machine purchase price in CZK.
        lifetime_hrs: Total expected lifetime in hours.
        maintenance_annual: Annual maintenance cost in CZK.
        energy_cost_per_hr: Energy cost per hour in CZK.
        working_hrs_per_year: Working hours per year (default 2000).

    Returns:
        Hourly rate in CZK.

    Raises:
        ValueError: If lifetime_hrs is zero or negative.
    """
    if lifetime_hrs <= 0:
        raise ValueError("Lifetime hours must be positive")

    depreciation_per_hr = purchase_price / lifetime_hrs
    maintenance_per_hr = maintenance_annual / working_hrs_per_year if working_hrs_per_year > 0 else 0.0
    return depreciation_per_hr + maintenance_per_hr + energy_cost_per_hr
