"""Tests for thermotransfer (TTR) calculation mode."""

import pytest

from label_calculator.core.calculator import calculate
from label_calculator.core.models import JobInput, MaterialInput, TaxConfig, TierInput


@pytest.mark.unit
def test_ttr_material_cost_positive(
    satin_with_ttr: MaterialInput,
    satin_tier_do200: TierInput,
    default_tax: TaxConfig,
) -> None:
    """TTR material cost must be positive."""
    job = JobInput(width=20, height=40, quantity=10, production_type="thermotransfer")
    result = calculate(job, satin_with_ttr, satin_tier_do200, default_tax)
    assert result.material_cost_raw > 0
    assert result.material_cost > 0


@pytest.mark.unit
def test_ttr_no_pruning_waste(
    satin_with_ttr: MaterialInput,
    default_tax: TaxConfig,
) -> None:
    """TTR ignores pruning waste — same result with/without."""
    tier_with_prune = TierInput(pieces_per_hour=800, margin_pct=320, waste_test_pct=10, waste_pruning_pct=30)
    tier_no_prune = TierInput(pieces_per_hour=800, margin_pct=320, waste_test_pct=10, waste_pruning_pct=0)
    job = JobInput(width=20, height=40, quantity=10, production_type="thermotransfer")

    r_with = calculate(job, satin_with_ttr, tier_with_prune, default_tax)
    r_without = calculate(job, satin_with_ttr, tier_no_prune, default_tax)

    assert r_with.material_cost_raw == pytest.approx(r_without.material_cost_raw, rel=1e-6)
    assert r_with.waste_pruning_pct == 0.0


@pytest.mark.unit
def test_ttr_roundup3_on_price_per_cm(
    satin_material: MaterialInput,
    satin_tier_do200: TierInput,
    default_tax: TaxConfig,
) -> None:
    """Price per cm uses ROUNDUP(..., 3) — ceil to 3 decimal places."""
    job = JobInput(width=20, height=40, quantity=10, production_type="thermotransfer")
    result = calculate(job, satin_material, satin_tier_do200, default_tax)
    # 615.89 / (0.9 × 20000) = 0.034216 → ceil3 = 0.035
    assert result.price_per_unit_area == pytest.approx(0.035, abs=0.001)


@pytest.mark.unit
def test_ttr_addon_adds_material_cost(
    satin_material: MaterialInput,
    satin_with_ttr: MaterialInput,
    satin_tier_do200: TierInput,
    default_tax: TaxConfig,
) -> None:
    """Adding a TTR addon increases material cost."""
    job = JobInput(width=20, height=40, quantity=10, production_type="thermotransfer")
    r_no_addon = calculate(job, satin_material, satin_tier_do200, default_tax)
    r_with_addon = calculate(job, satin_with_ttr, satin_tier_do200, default_tax)
    assert r_with_addon.material_cost_raw > r_no_addon.material_cost_raw


@pytest.mark.unit
def test_ttr_addon_doesnt_add_labor(
    satin_material: MaterialInput,
    satin_with_ttr: MaterialInput,
    satin_tier_do200: TierInput,
    default_tax: TaxConfig,
) -> None:
    """Addon does NOT add labor — same labor with or without."""
    job = JobInput(width=20, height=40, quantity=10, production_type="thermotransfer")
    r_no = calculate(job, satin_material, satin_tier_do200, default_tax)
    r_with = calculate(job, satin_with_ttr, satin_tier_do200, default_tax)
    assert r_no.labor_cost == r_with.labor_cost


@pytest.mark.unit
def test_ttr_labor_formula(
    satin_with_ttr: MaterialInput,
    satin_tier_do200: TierInput,
    default_tax: TaxConfig,
) -> None:
    """Labor = hourly_rate / pieces_per_hour."""
    job = JobInput(width=20, height=40, quantity=10, production_type="thermotransfer")
    result = calculate(job, satin_with_ttr, satin_tier_do200, default_tax, hourly_rate=810)
    assert result.labor_cost == pytest.approx(810 / 800, rel=1e-6)
