"""Tests for thermotransfer (TTR) calculation mode."""

import pytest

from label_calculator.core.calculator import calculate
from label_calculator.core.models import (
    AddonInput,
    JobInput,
    MachineInput,
    MaterialInput,
    MaterialMachineParams,
    TaxConfig,
    TierInput,
)


@pytest.mark.unit
def test_ttr_material_plus_addon_cost(
    satin_ribbon_with_addon: MaterialInput,
    ttr_printer: MachineInput,
    satin_ttr_params: MaterialMachineParams,
    satin_tier: TierInput,
    ttr_job_25x80: JobInput,
    default_tax: TaxConfig,
) -> None:
    """TTR: material cost + addon cost should both be positive."""
    result = calculate(
        job=ttr_job_25x80,
        material=satin_ribbon_with_addon,
        machine=ttr_printer,
        params=satin_ttr_params,
        tier=satin_tier,
        tax=default_tax,
    )
    assert result.material_cost > 0
    assert result.addon_cost > 0


@pytest.mark.unit
def test_ttr_machine_counted_once(
    satin_ribbon: MaterialInput,
    satin_ribbon_with_addon: MaterialInput,
    ttr_printer: MachineInput,
    satin_ttr_params: MaterialMachineParams,
    satin_tier: TierInput,
    ttr_job_25x80: JobInput,
) -> None:
    """Addon does NOT add machine time — machine counted once."""
    r_no_addon = calculate(
        job=ttr_job_25x80,
        material=satin_ribbon,
        machine=ttr_printer,
        params=satin_ttr_params,
        tier=satin_tier,
    )
    r_with_addon = calculate(
        job=ttr_job_25x80,
        material=satin_ribbon_with_addon,
        machine=ttr_printer,
        params=satin_ttr_params,
        tier=satin_tier,
    )
    assert r_no_addon.machine_cost == r_with_addon.machine_cost


@pytest.mark.unit
def test_ttr_operator_counted_once(
    satin_ribbon: MaterialInput,
    satin_ribbon_with_addon: MaterialInput,
    ttr_printer: MachineInput,
    satin_ttr_params: MaterialMachineParams,
    satin_tier: TierInput,
    ttr_job_25x80: JobInput,
) -> None:
    """Addon does NOT add operator time."""
    r_no_addon = calculate(
        job=ttr_job_25x80,
        material=satin_ribbon,
        machine=ttr_printer,
        params=satin_ttr_params,
        tier=satin_tier,
    )
    r_with_addon = calculate(
        job=ttr_job_25x80,
        material=satin_ribbon_with_addon,
        machine=ttr_printer,
        params=satin_ttr_params,
        tier=satin_tier,
    )
    assert r_no_addon.operator_cost == r_with_addon.operator_cost


@pytest.mark.unit
def test_ttr_kerf_is_zero(
    satin_ribbon_with_addon: MaterialInput,
    ttr_printer: MachineInput,
    satin_ttr_params: MaterialMachineParams,
    satin_tier: TierInput,
    ttr_job_25x80: JobInput,
) -> None:
    """TTR params kerf should be zero (no cutting)."""
    assert satin_ttr_params.kerf_mm == 0


@pytest.mark.unit
def test_ttr_waste_is_test_only(
    satin_ribbon_with_addon: MaterialInput,
    ttr_printer: MachineInput,
    satin_ttr_params: MaterialMachineParams,
    ttr_job_25x80: JobInput,
) -> None:
    """TTR waste has no pruning — only test pieces and test%."""
    tier_with_pruning = TierInput(
        pieces_per_hour=200.0,
        margin_pct=45.0,
        waste_test_pieces=3,
        waste_test_pct=10.0,
        waste_pruning_pct=20.0,  # this should be zeroed in TTR
    )
    result = calculate(
        job=ttr_job_25x80,
        material=satin_ribbon_with_addon,
        machine=ttr_printer,
        params=satin_ttr_params,
        tier=tier_with_pruning,
    )
    # TTR sets pruning to 0% internally — verify via checking that
    # waste_cost is less than it would be with pruning
    tier_no_pruning = TierInput(
        pieces_per_hour=200.0,
        margin_pct=45.0,
        waste_test_pieces=3,
        waste_test_pct=10.0,
        waste_pruning_pct=0.0,
    )
    result_ref = calculate(
        job=ttr_job_25x80,
        material=satin_ribbon_with_addon,
        machine=ttr_printer,
        params=satin_ttr_params,
        tier=tier_no_pruning,
    )
    # Both should be the same since TTR zeroes pruning
    assert result.waste_cost == pytest.approx(result_ref.waste_cost, rel=1e-3)


@pytest.mark.unit
def test_ttr_addon_width_autofill(silver_addon: AddonInput) -> None:
    """Addon sheet_width (ribbon width) should match expected value for auto-fill."""
    assert silver_addon.sheet_width == 25.0
