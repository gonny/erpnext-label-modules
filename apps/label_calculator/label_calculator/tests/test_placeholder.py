"""Placeholder tests — validate that the test pipeline is wired up correctly.

These tests do NOT require a running Frappe instance and are tagged ``unit``
so they run in the fast, database-free CI job.
"""

import pytest

from label_calculator.core.calculator import calculate
from label_calculator.core.models import CalcResult, JobInput, MaterialInput, TierInput


@pytest.mark.unit
def test_calculate_returns_calc_result(
    leatherette_material: MaterialInput,
    leatherette_tier_do30: TierInput,
) -> None:
    """calculate() should return a CalcResult for valid input."""
    job = JobInput(width=30, height=20, quantity=10, production_type="laser")
    result = calculate(job, leatherette_material, leatherette_tier_do30)
    assert isinstance(result, CalcResult)


@pytest.mark.unit
def test_calculate_total_price_positive(
    leatherette_material: MaterialInput,
    leatherette_tier_do30: TierInput,
) -> None:
    """Total price must be positive for valid inputs."""
    job = JobInput(width=30, height=20, quantity=10, production_type="laser")
    result = calculate(job, leatherette_material, leatherette_tier_do30)
    assert result.total_price > 0
    assert result.unit_price > 0
