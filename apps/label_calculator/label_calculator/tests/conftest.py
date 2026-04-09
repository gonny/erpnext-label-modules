"""Pytest configuration and shared fixtures for label_calculator tests."""

import pytest

from label_calculator.core.models import (
    AddonInput,
    JobInput,
    MaterialInput,
    TaxConfig,
    TierInput,
)

# ---------------------------------------------------------------------------
# Materials — production-accurate values from Excel/Odoo
# ---------------------------------------------------------------------------


@pytest.fixture
def leatherette_material() -> MaterialInput:
    """Koženka černo/stříbrná — 600×300mm sheet, 310 CZK incl. VAT."""
    return MaterialInput(
        purchase_price=310.0,
        purchase_vat_included=True,
        purchase_vat_pct=21.0,
        sheet_width=600.0,
        sheet_height=300.0,
        material_type="sheet",
        name="Koženka černo/stříbrná",
    )


@pytest.fixture
def silver_ttr_addon() -> AddonInput:
    """Stříbrná textilní TTR ribbon — 69mm × 200m, 441 CZK ex-VAT."""
    return AddonInput(
        purchase_price=441.0,
        purchase_vat_included=False,
        purchase_vat_pct=21.0,
        roll_width_mm=69.0,
        roll_length_m=200.0,
        color_name="stříbrný",
    )


@pytest.fixture
def satin_material() -> MaterialInput:
    """Satén bílá 20mm — 200m roll, 509 CZK ex-VAT."""
    return MaterialInput(
        purchase_price=509.0,
        purchase_vat_included=False,
        purchase_vat_pct=21.0,
        roll_width_mm=20.0,
        roll_length_m=200.0,
        material_type="roll",
        name="Satén bílá 20mm",
    )


@pytest.fixture
def satin_with_ttr(satin_material: MaterialInput, silver_ttr_addon: AddonInput) -> MaterialInput:
    """Satén bílá 20mm + TTR stříbrná addon."""
    return MaterialInput(
        purchase_price=satin_material.purchase_price,
        purchase_vat_included=satin_material.purchase_vat_included,
        purchase_vat_pct=satin_material.purchase_vat_pct,
        roll_width_mm=satin_material.roll_width_mm,
        roll_length_m=satin_material.roll_length_m,
        material_type=satin_material.material_type,
        name=satin_material.name,
        addons=[silver_ttr_addon],
    )


# ---------------------------------------------------------------------------
# Tiers — production-accurate values
# ---------------------------------------------------------------------------


@pytest.fixture
def leatherette_tier_do30() -> TierInput:
    """Koženka tier "Do 30": 1-29 pcs, 80 pcs/hr, 320% margin."""
    return TierInput(
        pieces_per_hour=80,
        margin_pct=320,
        waste_test_pct=10,
        waste_pruning_pct=15,
        min_quantity=1,
        max_quantity=29,
    )


@pytest.fixture
def leatherette_tier_do100() -> TierInput:
    """Koženka tier "Do 100": 30-99 pcs, 100 pcs/hr, 310% margin."""
    return TierInput(
        pieces_per_hour=100,
        margin_pct=310,
        waste_test_pct=10,
        waste_pruning_pct=15,
        min_quantity=30,
        max_quantity=99,
    )


@pytest.fixture
def leatherette_tier_do500() -> TierInput:
    """Koženka tier "Do 500": 100-499 pcs, 120 pcs/hr, 300% margin."""
    return TierInput(
        pieces_per_hour=120,
        margin_pct=300,
        waste_test_pct=10,
        waste_pruning_pct=12,
        min_quantity=100,
        max_quantity=499,
    )


@pytest.fixture
def satin_tier_do200() -> TierInput:
    """Satén tier "Do 200": 1-199 pcs, 800 pcs/hr, 320% margin."""
    return TierInput(
        pieces_per_hour=800,
        margin_pct=320,
        waste_test_pct=10,
        waste_pruning_pct=30,  # ignored for TTR
        min_quantity=1,
        max_quantity=199,
    )


# ---------------------------------------------------------------------------
# Tax
# ---------------------------------------------------------------------------


@pytest.fixture
def default_tax() -> TaxConfig:
    """Default: 15% income tax, grossup enabled."""
    return TaxConfig(income_tax_rate=15.0, apply_material_grossup=True)


@pytest.fixture
def no_tax() -> TaxConfig:
    """Grossup disabled."""
    return TaxConfig(income_tax_rate=15.0, apply_material_grossup=False)


# ---------------------------------------------------------------------------
# Jobs
# ---------------------------------------------------------------------------


@pytest.fixture
def laser_job_30x20() -> JobInput:
    """Laser job: 30×20mm, 10 pcs."""
    return JobInput(width=30.0, height=20.0, quantity=10, production_type="laser")


@pytest.fixture
def ttr_job_20x40() -> JobInput:
    """TTR job: 20×40mm (ribbon width × print length), 10 pcs."""
    return JobInput(width=20.0, height=40.0, quantity=10, production_type="thermotransfer")
