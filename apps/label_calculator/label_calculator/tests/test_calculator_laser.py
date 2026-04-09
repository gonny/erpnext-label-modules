"""Tests for laser calculation mode."""

import math

import pytest

from label_calculator.core.calculator import calculate
from label_calculator.core.models import CalcResult, JobInput, MaterialInput, TaxConfig, TierInput


@pytest.mark.unit
def test_laser_returns_calc_result(
    leatherette_material: MaterialInput,
    leatherette_tier_do30: TierInput,
    default_tax: TaxConfig,
) -> None:
    """calculate() returns a CalcResult for laser mode."""
    job = JobInput(width=30, height=20, quantity=10, production_type="laser")
    result = calculate(job, leatherette_material, leatherette_tier_do30, default_tax)
    assert isinstance(result, CalcResult)


@pytest.mark.unit
def test_laser_material_cost_positive(
    leatherette_material: MaterialInput,
    leatherette_tier_do30: TierInput,
    default_tax: TaxConfig,
) -> None:
    """Material cost (raw and with margin) must be positive."""
    job = JobInput(width=30, height=20, quantity=10, production_type="laser")
    result = calculate(job, leatherette_material, leatherette_tier_do30, default_tax)
    assert result.material_cost_raw > 0
    assert result.material_cost > 0


@pytest.mark.unit
def test_laser_material_cost_formula(
    leatherette_material: MaterialInput,
    leatherette_tier_do30: TierInput,
    default_tax: TaxConfig,
) -> None:
    """material_cost = material_cost_raw × (1 + margin/100)."""
    job = JobInput(width=30, height=20, quantity=10, production_type="laser")
    result = calculate(job, leatherette_material, leatherette_tier_do30, default_tax)
    expected = result.material_cost_raw * (1 + leatherette_tier_do30.margin_pct / 100)
    assert result.material_cost == pytest.approx(expected, rel=1e-6)


@pytest.mark.unit
def test_laser_margin_on_material_only(
    leatherette_material: MaterialInput,
    leatherette_tier_do30: TierInput,
    default_tax: TaxConfig,
) -> None:
    """Margin applies to material, NOT to labor."""
    job = JobInput(width=30, height=20, quantity=10, production_type="laser")
    result = calculate(job, leatherette_material, leatherette_tier_do30, default_tax)
    # unit_price = material_with_margin + labor (no margin on labor), rounded up
    raw_sum = result.material_cost + result.labor_cost
    assert result.unit_price == pytest.approx(raw_sum, abs=0.1)  # within rounding


@pytest.mark.unit
def test_laser_labor_formula(
    leatherette_material: MaterialInput,
    leatherette_tier_do30: TierInput,
    default_tax: TaxConfig,
) -> None:
    """labor_cost = hourly_rate / pieces_per_hour."""
    job = JobInput(width=30, height=20, quantity=10, production_type="laser")
    result = calculate(job, leatherette_material, leatherette_tier_do30, default_tax, hourly_rate=810)
    expected_labor = 810 / 80  # 10.125
    assert result.labor_cost == pytest.approx(expected_labor, rel=1e-6)


@pytest.mark.unit
def test_laser_unit_price_rounded_up(
    leatherette_material: MaterialInput,
    leatherette_tier_do30: TierInput,
    default_tax: TaxConfig,
) -> None:
    """Unit price rounded UP to 0.10 CZK."""
    job = JobInput(width=30, height=20, quantity=10, production_type="laser")
    result = calculate(job, leatherette_material, leatherette_tier_do30, default_tax)
    expected = math.ceil((result.material_cost + result.labor_cost) * 10) / 10
    assert result.unit_price == expected


@pytest.mark.unit
def test_laser_total_is_unit_times_quantity(
    leatherette_material: MaterialInput,
    leatherette_tier_do30: TierInput,
    default_tax: TaxConfig,
) -> None:
    """total_price = unit_price × quantity."""
    job = JobInput(width=30, height=20, quantity=10, production_type="laser")
    result = calculate(job, leatherette_material, leatherette_tier_do30, default_tax)
    assert result.total_price == pytest.approx(result.unit_price * 10, rel=1e-6)


@pytest.mark.unit
def test_laser_zero_dims_raises(
    leatherette_material: MaterialInput,
    leatherette_tier_do30: TierInput,
) -> None:
    """Zero dimensions raise ValueError."""
    job = JobInput(width=0, height=20, quantity=10, production_type="laser")
    with pytest.raises(ValueError, match="positive"):
        calculate(job, leatherette_material, leatherette_tier_do30)


@pytest.mark.unit
def test_laser_copies_multiply_total(
    leatherette_material: MaterialInput,
    leatherette_tier_do30: TierInput,
    default_tax: TaxConfig,
) -> None:
    """Multiple copies multiply total_price."""
    job_1 = JobInput(width=30, height=20, quantity=10, copies=1, production_type="laser")
    job_2 = JobInput(width=30, height=20, quantity=10, copies=2, production_type="laser")
    r1 = calculate(job_1, leatherette_material, leatherette_tier_do30, default_tax)
    r2 = calculate(job_2, leatherette_material, leatherette_tier_do30, default_tax)
    # Same unit price, double total
    assert r1.unit_price == r2.unit_price
    assert r2.total_price == pytest.approx(r1.total_price * 2, rel=1e-6)
