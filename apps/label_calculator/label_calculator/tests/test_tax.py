"""Tests for material gross-up (income tax) logic."""

import pytest

from label_calculator.core.calculator import calculate
from label_calculator.core.models import JobInput, MaterialInput, TaxConfig, TierInput


@pytest.mark.unit
def test_grossup_increases_material_cost(
    leatherette_material: MaterialInput,
    leatherette_tier_do30: TierInput,
) -> None:
    """Gross-up increases material cost vs no gross-up."""
    job = JobInput(width=30, height=20, quantity=10, production_type="laser")
    tax_on = TaxConfig(income_tax_rate=15.0, apply_material_grossup=True)
    tax_off = TaxConfig(income_tax_rate=15.0, apply_material_grossup=False)

    r_on = calculate(job, leatherette_material, leatherette_tier_do30, tax_on)
    r_off = calculate(job, leatherette_material, leatherette_tier_do30, tax_off)
    assert r_on.material_cost_raw > r_off.material_cost_raw


@pytest.mark.unit
def test_grossup_does_not_affect_labor(
    leatherette_material: MaterialInput,
    leatherette_tier_do30: TierInput,
) -> None:
    """Gross-up applies to material, NOT labor."""
    job = JobInput(width=30, height=20, quantity=10, production_type="laser")
    tax_on = TaxConfig(income_tax_rate=15.0, apply_material_grossup=True)
    tax_off = TaxConfig(income_tax_rate=15.0, apply_material_grossup=False)

    r_on = calculate(job, leatherette_material, leatherette_tier_do30, tax_on)
    r_off = calculate(job, leatherette_material, leatherette_tier_do30, tax_off)
    assert r_on.labor_cost == r_off.labor_cost


@pytest.mark.unit
def test_grossup_disabled_no_change(
    leatherette_material: MaterialInput,
    leatherette_tier_do30: TierInput,
) -> None:
    """Disabled grossup = same as zero rate."""
    job = JobInput(width=30, height=20, quantity=10, production_type="laser")
    tax_disabled = TaxConfig(income_tax_rate=15.0, apply_material_grossup=False)
    tax_zero = TaxConfig(income_tax_rate=0.0, apply_material_grossup=True)

    r_disabled = calculate(job, leatherette_material, leatherette_tier_do30, tax_disabled)
    r_zero = calculate(job, leatherette_material, leatherette_tier_do30, tax_zero)
    assert r_disabled.material_cost_raw == pytest.approx(r_zero.material_cost_raw, rel=1e-6)


@pytest.mark.unit
def test_grossup_15pct_divides_by_085(
    leatherette_material: MaterialInput,
    leatherette_tier_do30: TierInput,
) -> None:
    """15% gross-up divides material cost by 0.85."""
    job = JobInput(width=30, height=20, quantity=10, production_type="laser")
    tax_on = TaxConfig(income_tax_rate=15.0, apply_material_grossup=True)
    tax_off = TaxConfig(income_tax_rate=15.0, apply_material_grossup=False)

    r_on = calculate(job, leatherette_material, leatherette_tier_do30, tax_on)
    r_off = calculate(job, leatherette_material, leatherette_tier_do30, tax_off)
    expected = r_off.material_cost_raw / 0.85
    assert r_on.material_cost_raw == pytest.approx(expected, rel=1e-3)


@pytest.mark.unit
def test_grossup_zero_rate_no_change(
    leatherette_material: MaterialInput,
    leatherette_tier_do30: TierInput,
) -> None:
    """Zero tax rate with grossup enabled — no change."""
    job = JobInput(width=30, height=20, quantity=10, production_type="laser")
    tax_zero = TaxConfig(income_tax_rate=0.0, apply_material_grossup=True)
    tax_off = TaxConfig(income_tax_rate=15.0, apply_material_grossup=False)

    r_zero = calculate(job, leatherette_material, leatherette_tier_do30, tax_zero)
    r_off = calculate(job, leatherette_material, leatherette_tier_do30, tax_off)
    assert r_zero.material_cost_raw == pytest.approx(r_off.material_cost_raw, rel=1e-6)
