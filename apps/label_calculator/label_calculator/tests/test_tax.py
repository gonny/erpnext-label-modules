"""Tests for material gross-up (income tax) logic."""

import pytest

from label_calculator.core.calculator import calculate
from label_calculator.core.models import (
    JobInput,
    MachineInput,
    MaterialInput,
    MaterialMachineParams,
    TaxConfig,
    TierInput,
)


@pytest.mark.unit
def test_grossup_increases_material_cost(
    vinyl_material: MaterialInput,
    epilog_laser: MachineInput,
    vinyl_laser_params: MaterialMachineParams,
    small_batch_tier: TierInput,
    laser_job_50x30: JobInput,
) -> None:
    """Gross-up should increase material cost compared to no gross-up."""
    tax_on = TaxConfig(income_tax_rate=15.0, apply_material_grossup=True)
    tax_off = TaxConfig(income_tax_rate=15.0, apply_material_grossup=False)

    r_on = calculate(
        job=laser_job_50x30,
        material=vinyl_material,
        machine=epilog_laser,
        params=vinyl_laser_params,
        tier=small_batch_tier,
        tax=tax_on,
    )
    r_off = calculate(
        job=laser_job_50x30,
        material=vinyl_material,
        machine=epilog_laser,
        params=vinyl_laser_params,
        tier=small_batch_tier,
        tax=tax_off,
    )
    assert r_on.material_cost > r_off.material_cost


@pytest.mark.unit
def test_grossup_does_not_affect_machine_cost(
    vinyl_material: MaterialInput,
    epilog_laser: MachineInput,
    vinyl_laser_params: MaterialMachineParams,
    small_batch_tier: TierInput,
    laser_job_50x30: JobInput,
) -> None:
    """Gross-up applies only to material/addon cost, NOT machine cost."""
    tax_on = TaxConfig(income_tax_rate=15.0, apply_material_grossup=True)
    tax_off = TaxConfig(income_tax_rate=15.0, apply_material_grossup=False)

    r_on = calculate(
        job=laser_job_50x30,
        material=vinyl_material,
        machine=epilog_laser,
        params=vinyl_laser_params,
        tier=small_batch_tier,
        tax=tax_on,
    )
    r_off = calculate(
        job=laser_job_50x30,
        material=vinyl_material,
        machine=epilog_laser,
        params=vinyl_laser_params,
        tier=small_batch_tier,
        tax=tax_off,
    )
    assert r_on.machine_cost == r_off.machine_cost


@pytest.mark.unit
def test_grossup_disabled_no_change(
    vinyl_material: MaterialInput,
    epilog_laser: MachineInput,
    vinyl_laser_params: MaterialMachineParams,
    small_batch_tier: TierInput,
    laser_job_50x30: JobInput,
) -> None:
    """With grossup disabled, material cost is unchanged regardless of tax rate."""
    tax_disabled = TaxConfig(income_tax_rate=15.0, apply_material_grossup=False)
    tax_zero = TaxConfig(income_tax_rate=0.0, apply_material_grossup=True)

    r_disabled = calculate(
        job=laser_job_50x30,
        material=vinyl_material,
        machine=epilog_laser,
        params=vinyl_laser_params,
        tier=small_batch_tier,
        tax=tax_disabled,
    )
    r_zero = calculate(
        job=laser_job_50x30,
        material=vinyl_material,
        machine=epilog_laser,
        params=vinyl_laser_params,
        tier=small_batch_tier,
        tax=tax_zero,
    )
    assert r_disabled.material_cost == r_zero.material_cost


@pytest.mark.unit
def test_grossup_15pct_divides_by_085(
    vinyl_material: MaterialInput,
    epilog_laser: MachineInput,
    vinyl_laser_params: MaterialMachineParams,
    small_batch_tier: TierInput,
    laser_job_50x30: JobInput,
) -> None:
    """15% gross-up divides material cost by 0.85."""
    tax_on = TaxConfig(income_tax_rate=15.0, apply_material_grossup=True)
    tax_off = TaxConfig(income_tax_rate=15.0, apply_material_grossup=False)

    r_on = calculate(
        job=laser_job_50x30,
        material=vinyl_material,
        machine=epilog_laser,
        params=vinyl_laser_params,
        tier=small_batch_tier,
        tax=tax_on,
    )
    r_off = calculate(
        job=laser_job_50x30,
        material=vinyl_material,
        machine=epilog_laser,
        params=vinyl_laser_params,
        tier=small_batch_tier,
        tax=tax_off,
    )
    # material_cost_on = material_cost_off / 0.85
    expected = r_off.material_cost / 0.85
    assert r_on.material_cost == pytest.approx(expected, rel=1e-3)


@pytest.mark.unit
def test_grossup_zero_rate_no_change(
    vinyl_material: MaterialInput,
    epilog_laser: MachineInput,
    vinyl_laser_params: MaterialMachineParams,
    small_batch_tier: TierInput,
    laser_job_50x30: JobInput,
) -> None:
    """Zero tax rate with grossup enabled should not change material cost."""
    tax_zero = TaxConfig(income_tax_rate=0.0, apply_material_grossup=True)
    tax_off = TaxConfig(income_tax_rate=15.0, apply_material_grossup=False)

    r_zero = calculate(
        job=laser_job_50x30,
        material=vinyl_material,
        machine=epilog_laser,
        params=vinyl_laser_params,
        tier=small_batch_tier,
        tax=tax_zero,
    )
    r_off = calculate(
        job=laser_job_50x30,
        material=vinyl_material,
        machine=epilog_laser,
        params=vinyl_laser_params,
        tier=small_batch_tier,
        tax=tax_off,
    )
    assert r_zero.material_cost == pytest.approx(r_off.material_cost, rel=1e-3)
