"""Pytest configuration and shared fixtures for label_calculator tests."""

import pytest

from label_calculator.core.models import (
    AddonInput,
    JobInput,
    MachineInput,
    MaterialInput,
    MaterialMachineParams,
    TaxConfig,
    TierInput,
)

# ---------------------------------------------------------------------------
# Materials
# ---------------------------------------------------------------------------


@pytest.fixture
def vinyl_material() -> MaterialInput:
    """White vinyl sheet 305×610mm, 45 CZK per sheet."""
    return MaterialInput(
        price_per_unit=45.0,
        sheet_width=305.0,
        sheet_height=610.0,
        material_type="Sheet",
        cut_margin_pct=8.0,
        name="Bílý vinyl",
        color_name="Bílá",
    )


@pytest.fixture
def satin_ribbon() -> MaterialInput:
    """Satin ribbon 25mm, roll 100m, 0.80 CZK/m."""
    return MaterialInput(
        price_per_unit=0.80,
        sheet_width=25.0,
        sheet_height=100_000.0,  # 100m in mm
        material_type="Roll",
        cut_margin_pct=0.0,
        name="Saténová stuha",
        color_name="Bílá",
    )


@pytest.fixture
def satin_ribbon_with_addon() -> MaterialInput:
    """Satin ribbon with silver TTR addon."""
    return MaterialInput(
        price_per_unit=0.80,
        sheet_width=25.0,
        sheet_height=100_000.0,
        material_type="Roll",
        cut_margin_pct=0.0,
        name="Saténová stuha",
        color_name="Bílá",
        addons=[
            AddonInput(
                price_per_unit=0.90,
                sheet_width=25.0,
                name="Páska stříbrná",
                color_name="stříbrný",
            ),
        ],
    )


@pytest.fixture
def silver_addon() -> AddonInput:
    """Silver TTR ribbon addon."""
    return AddonInput(
        price_per_unit=0.90,
        sheet_width=25.0,
        name="Páska stříbrná",
        color_name="stříbrný",
    )


# ---------------------------------------------------------------------------
# Machines
# ---------------------------------------------------------------------------


@pytest.fixture
def epilog_laser() -> MachineInput:
    """Epilog Laser — hourly rate ~42.17 CZK."""
    return MachineInput(hourly_rate=42.1667)


@pytest.fixture
def ttr_printer() -> MachineInput:
    """TTR Printer — hourly rate ~13.5 CZK."""
    return MachineInput(hourly_rate=13.5)


# ---------------------------------------------------------------------------
# Material Machine Params
# ---------------------------------------------------------------------------


@pytest.fixture
def vinyl_laser_params() -> MaterialMachineParams:
    """White vinyl on Epilog Laser."""
    return MaterialMachineParams(cut_speed_mm_per_sec=45.0, kerf_mm=0.15)


@pytest.fixture
def satin_ttr_params() -> MaterialMachineParams:
    """Satin ribbon on TTR printer — zero kerf."""
    return MaterialMachineParams(cut_speed_mm_per_sec=100.0, kerf_mm=0.0)


# ---------------------------------------------------------------------------
# Tiers
# ---------------------------------------------------------------------------


@pytest.fixture
def prototype_tier() -> TierInput:
    """Prototype tier: 1-10 pcs, high margin, high waste."""
    return TierInput(
        pieces_per_hour=150.0,
        margin_pct=50.0,
        waste_test_pieces=5,
        waste_test_pct=15.0,
        waste_pruning_pct=12.0,
    )


@pytest.fixture
def small_batch_tier() -> TierInput:
    """Small batch tier: 11-100 pcs."""
    return TierInput(
        pieces_per_hour=400.0,
        margin_pct=35.0,
        waste_test_pieces=3,
        waste_test_pct=10.0,
        waste_pruning_pct=10.0,
    )


@pytest.fixture
def standard_tier() -> TierInput:
    """Standard tier: 101-500 pcs."""
    return TierInput(
        pieces_per_hour=800.0,
        margin_pct=25.0,
        waste_test_pieces=2,
        waste_test_pct=8.0,
        waste_pruning_pct=8.0,
    )


@pytest.fixture
def large_batch_tier() -> TierInput:
    """Large batch tier: 501+ pcs."""
    return TierInput(
        pieces_per_hour=1200.0,
        margin_pct=18.0,
        waste_test_pieces=1,
        waste_test_pct=5.0,
        waste_pruning_pct=5.0,
    )


@pytest.fixture
def satin_tier() -> TierInput:
    """Satin TTR tier: no pruning waste."""
    return TierInput(
        pieces_per_hour=200.0,
        margin_pct=45.0,
        waste_test_pieces=3,
        waste_test_pct=10.0,
        waste_pruning_pct=0.0,
    )


# ---------------------------------------------------------------------------
# Tax
# ---------------------------------------------------------------------------


@pytest.fixture
def default_tax() -> TaxConfig:
    """Default tax config: 15% income tax, grossup enabled."""
    return TaxConfig(income_tax_rate=15.0, apply_material_grossup=True)


@pytest.fixture
def no_tax() -> TaxConfig:
    """Tax config with grossup disabled."""
    return TaxConfig(income_tax_rate=15.0, apply_material_grossup=False)


# ---------------------------------------------------------------------------
# Jobs
# ---------------------------------------------------------------------------


@pytest.fixture
def laser_job_50x30() -> JobInput:
    """Laser job: 50×30mm, 100 pcs."""
    return JobInput(
        width=50.0,
        height=30.0,
        quantity=100,
        copies=1,
        production_type="laser",
        operator_rate=200.0,
        setup_time_min=5.0,
        operator_time_per_unit_sec=0.0,
    )


@pytest.fixture
def ttr_job_25x80() -> JobInput:
    """TTR job: 25×80mm, 100 pcs."""
    return JobInput(
        width=25.0,
        height=80.0,
        quantity=100,
        copies=1,
        production_type="thermotransfer",
        operator_rate=200.0,
        setup_time_min=5.0,
        operator_time_per_unit_sec=0.0,
    )
