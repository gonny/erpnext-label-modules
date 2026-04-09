"""Placeholder tests — validate that the test pipeline is wired up correctly.

These tests do NOT require a running Frappe instance and are tagged ``unit``
so they run in the fast, database-free CI job.
"""

import pytest

from label_calculator.core.calculator import calculate
from label_calculator.core.models import (
    CalcResult,
    JobInput,
    MachineInput,
    MaterialInput,
    MaterialMachineParams,
    TierInput,
)


@pytest.mark.unit
def test_calculate_returns_calc_result(
    vinyl_material: MaterialInput,
    epilog_laser: MachineInput,
    vinyl_laser_params: MaterialMachineParams,
    small_batch_tier: TierInput,
    laser_job_50x30: JobInput,
) -> None:
    """calculate() should return a CalcResult for valid input."""
    result = calculate(
        job=laser_job_50x30,
        material=vinyl_material,
        machine=epilog_laser,
        params=vinyl_laser_params,
        tier=small_batch_tier,
    )
    assert isinstance(result, CalcResult)


@pytest.mark.unit
def test_calculate_total_price_positive(
    vinyl_material: MaterialInput,
    epilog_laser: MachineInput,
    vinyl_laser_params: MaterialMachineParams,
    small_batch_tier: TierInput,
    laser_job_50x30: JobInput,
) -> None:
    """Total price must be positive for valid inputs."""
    result = calculate(
        job=laser_job_50x30,
        material=vinyl_material,
        machine=epilog_laser,
        params=vinyl_laser_params,
        tier=small_batch_tier,
    )
    assert result.total_price > 0
    assert result.unit_price > 0
