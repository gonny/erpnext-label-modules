"""Tests for laser calculation mode."""

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
def test_labels_per_sheet(
    vinyl_material: MaterialInput,
    epilog_laser: MachineInput,
    vinyl_laser_params: MaterialMachineParams,
    small_batch_tier: TierInput,
    laser_job_50x30: JobInput,
) -> None:
    """Labels per sheet for 305×610 sheet, 50×30mm labels, kerf=0.15."""
    result = calculate(
        job=laser_job_50x30,
        material=vinyl_material,
        machine=epilog_laser,
        params=vinyl_laser_params,
        tier=small_batch_tier,
    )
    # 305/(50+0.15)=6, 610/(30+0.15)=20 → 120
    assert result.labels_per_sheet == 120


@pytest.mark.unit
def test_sheets_needed(
    vinyl_material: MaterialInput,
    epilog_laser: MachineInput,
    vinyl_laser_params: MaterialMachineParams,
    small_batch_tier: TierInput,
    laser_job_50x30: JobInput,
) -> None:
    """Sheets needed must account for waste."""
    result = calculate(
        job=laser_job_50x30,
        material=vinyl_material,
        machine=epilog_laser,
        params=vinyl_laser_params,
        tier=small_batch_tier,
    )
    assert result.sheets_needed >= 1


@pytest.mark.unit
def test_material_cost(
    vinyl_material: MaterialInput,
    epilog_laser: MachineInput,
    vinyl_laser_params: MaterialMachineParams,
    small_batch_tier: TierInput,
    laser_job_50x30: JobInput,
    default_tax: TaxConfig,
) -> None:
    """Material cost must be positive and include gross-up."""
    result = calculate(
        job=laser_job_50x30,
        material=vinyl_material,
        machine=epilog_laser,
        params=vinyl_laser_params,
        tier=small_batch_tier,
        tax=default_tax,
    )
    assert result.material_cost > 0


@pytest.mark.unit
def test_machine_cost_positive(
    vinyl_material: MaterialInput,
    epilog_laser: MachineInput,
    vinyl_laser_params: MaterialMachineParams,
    small_batch_tier: TierInput,
    laser_job_50x30: JobInput,
) -> None:
    """Machine cost must be positive when hourly rate > 0."""
    result = calculate(
        job=laser_job_50x30,
        material=vinyl_material,
        machine=epilog_laser,
        params=vinyl_laser_params,
        tier=small_batch_tier,
    )
    assert result.machine_cost > 0


@pytest.mark.unit
def test_operator_cost_includes_setup(
    vinyl_material: MaterialInput,
    epilog_laser: MachineInput,
    vinyl_laser_params: MaterialMachineParams,
    small_batch_tier: TierInput,
) -> None:
    """Operator cost should include setup time."""
    job_with_setup = JobInput(
        width=50,
        height=30,
        quantity=100,
        copies=1,
        production_type="laser",
        operator_rate=200.0,
        setup_time_min=30.0,
        operator_time_per_unit_sec=0.0,
    )
    result = calculate(
        job=job_with_setup,
        material=vinyl_material,
        machine=epilog_laser,
        params=vinyl_laser_params,
        tier=small_batch_tier,
    )
    # 30 min setup = 0.5 hrs × 200 = 100 CZK minimum
    assert result.operator_cost >= 100.0


@pytest.mark.unit
def test_waste_cost(
    vinyl_material: MaterialInput,
    epilog_laser: MachineInput,
    vinyl_laser_params: MaterialMachineParams,
    prototype_tier: TierInput,
) -> None:
    """Waste cost must be positive when tier has waste params."""
    job = JobInput(
        width=50,
        height=30,
        quantity=5,
        copies=1,
        production_type="laser",
        operator_rate=200.0,
        setup_time_min=5.0,
        operator_time_per_unit_sec=0.0,
    )
    result = calculate(
        job=job,
        material=vinyl_material,
        machine=epilog_laser,
        params=vinyl_laser_params,
        tier=prototype_tier,
    )
    assert result.waste_cost > 0


@pytest.mark.unit
def test_margin_applied(
    vinyl_material: MaterialInput,
    epilog_laser: MachineInput,
    vinyl_laser_params: MaterialMachineParams,
    small_batch_tier: TierInput,
    laser_job_50x30: JobInput,
) -> None:
    """Margin amount must be positive with margin_pct > 0."""
    result = calculate(
        job=laser_job_50x30,
        material=vinyl_material,
        machine=epilog_laser,
        params=vinyl_laser_params,
        tier=small_batch_tier,
    )
    assert result.margin_amount > 0
    assert result.margin_amount == pytest.approx(result.subtotal * small_batch_tier.margin_pct / 100, rel=1e-3)


@pytest.mark.unit
def test_total_is_subtotal_plus_margin(
    vinyl_material: MaterialInput,
    epilog_laser: MachineInput,
    vinyl_laser_params: MaterialMachineParams,
    small_batch_tier: TierInput,
    laser_job_50x30: JobInput,
) -> None:
    """Total price = subtotal + margin_amount."""
    result = calculate(
        job=laser_job_50x30,
        material=vinyl_material,
        machine=epilog_laser,
        params=vinyl_laser_params,
        tier=small_batch_tier,
    )
    assert result.total_price == pytest.approx(result.subtotal + result.margin_amount, rel=1e-3)


@pytest.mark.unit
def test_unit_price(
    vinyl_material: MaterialInput,
    epilog_laser: MachineInput,
    vinyl_laser_params: MaterialMachineParams,
    small_batch_tier: TierInput,
    laser_job_50x30: JobInput,
) -> None:
    """Unit price = total_price / quantity."""
    result = calculate(
        job=laser_job_50x30,
        material=vinyl_material,
        machine=epilog_laser,
        params=vinyl_laser_params,
        tier=small_batch_tier,
    )
    expected_unit = result.total_price / laser_job_50x30.quantity
    assert result.unit_price == pytest.approx(expected_unit, rel=1e-3)


@pytest.mark.unit
def test_single_unit(
    vinyl_material: MaterialInput,
    epilog_laser: MachineInput,
    vinyl_laser_params: MaterialMachineParams,
    prototype_tier: TierInput,
) -> None:
    """Single label calculation should work."""
    job = JobInput(
        width=50,
        height=30,
        quantity=1,
        copies=1,
        production_type="laser",
        operator_rate=200.0,
        setup_time_min=5.0,
        operator_time_per_unit_sec=0.0,
    )
    result = calculate(
        job=job,
        material=vinyl_material,
        machine=epilog_laser,
        params=vinyl_laser_params,
        tier=prototype_tier,
    )
    assert result.unit_price > 0
    assert result.total_price == pytest.approx(result.unit_price, rel=1e-3)


@pytest.mark.unit
def test_large_batch_cheaper_per_unit(
    vinyl_material: MaterialInput,
    epilog_laser: MachineInput,
    vinyl_laser_params: MaterialMachineParams,
    prototype_tier: TierInput,
    large_batch_tier: TierInput,
) -> None:
    """Large batch should have cheaper unit price than prototype."""
    small_job = JobInput(
        width=50,
        height=30,
        quantity=5,
        copies=1,
        production_type="laser",
        operator_rate=200.0,
        setup_time_min=5.0,
        operator_time_per_unit_sec=0.0,
    )
    large_job = JobInput(
        width=50,
        height=30,
        quantity=1000,
        copies=1,
        production_type="laser",
        operator_rate=200.0,
        setup_time_min=5.0,
        operator_time_per_unit_sec=0.0,
    )
    r_small = calculate(
        job=small_job,
        material=vinyl_material,
        machine=epilog_laser,
        params=vinyl_laser_params,
        tier=prototype_tier,
    )
    r_large = calculate(
        job=large_job,
        material=vinyl_material,
        machine=epilog_laser,
        params=vinyl_laser_params,
        tier=large_batch_tier,
    )
    assert r_large.unit_price < r_small.unit_price


@pytest.mark.unit
def test_zero_dimensions_raises(
    vinyl_material: MaterialInput,
    epilog_laser: MachineInput,
    vinyl_laser_params: MaterialMachineParams,
    small_batch_tier: TierInput,
) -> None:
    """Zero dimensions should raise ValueError."""
    job = JobInput(
        width=0,
        height=30,
        quantity=100,
        copies=1,
        production_type="laser",
        operator_rate=200.0,
    )
    with pytest.raises(ValueError, match="positive"):
        calculate(
            job=job,
            material=vinyl_material,
            machine=epilog_laser,
            params=vinyl_laser_params,
            tier=small_batch_tier,
        )


@pytest.mark.unit
def test_multiple_copies_increases_cost(
    vinyl_material: MaterialInput,
    epilog_laser: MachineInput,
    vinyl_laser_params: MaterialMachineParams,
    small_batch_tier: TierInput,
) -> None:
    """Multiple copies should increase total cost."""
    job_1copy = JobInput(
        width=50,
        height=30,
        quantity=100,
        copies=1,
        production_type="laser",
        operator_rate=200.0,
        setup_time_min=5.0,
    )
    job_2copies = JobInput(
        width=50,
        height=30,
        quantity=100,
        copies=2,
        production_type="laser",
        operator_rate=200.0,
        setup_time_min=5.0,
    )
    r1 = calculate(
        job=job_1copy,
        material=vinyl_material,
        machine=epilog_laser,
        params=vinyl_laser_params,
        tier=small_batch_tier,
    )
    r2 = calculate(
        job=job_2copies,
        material=vinyl_material,
        machine=epilog_laser,
        params=vinyl_laser_params,
        tier=small_batch_tier,
    )
    assert r2.total_price > r1.total_price
