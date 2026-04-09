"""Frozen regression tests matching production Excel/Odoo values.

These tests validate exact numerical outputs against the production
Excel spreadsheet. Changes to the calculation engine MUST NOT break
these values.
"""

import pytest

from label_calculator.core.calculator import calculate
from label_calculator.core.models import AddonInput, JobInput, MaterialInput, TaxConfig, TierInput


@pytest.mark.unit
class TestExcelRegression:
    """Frozen regression tests matching production Excel/Odoo values."""

    def test_leatherette_30x20_10pcs_laser(self) -> None:
        """Test 15: Koženka černo/stříbrná 30×20mm, 10 ks, laser.

        Tier "Do 30": 80 pcs/hr, margin 320%, test 10%, prune 15%.
        Material: 600×300mm sheet, 310 CZK incl. VAT.
        Global rate: 810 CZK/hr, tax 15%.
        """
        material = MaterialInput(
            purchase_price=310.0,
            purchase_vat_included=True,
            purchase_vat_pct=21.0,
            sheet_width=600.0,
            sheet_height=300.0,
            material_type="sheet",
            name="Koženka černo/stříbrná",
        )
        tier = TierInput(
            pieces_per_hour=80,
            margin_pct=320,
            waste_test_pct=10,
            waste_pruning_pct=15,
        )
        job = JobInput(width=30, height=20, quantity=10, production_type="laser")
        tax = TaxConfig(income_tax_rate=15, apply_material_grossup=True)

        result = calculate(job, material, tier, tax, hourly_rate=810)

        assert result.material_cost_raw == pytest.approx(1.589, abs=0.001)
        assert result.material_cost == pytest.approx(6.674, abs=0.01)
        assert result.labor_cost == pytest.approx(10.125, abs=0.001)
        assert result.unit_price == 16.80

    def test_satin_ttr_silver_20x40_10pcs(self) -> None:
        """Test 16: Satén bílá 20mm + TTR stříbrná, 40mm potisk, 10 ks.

        Tier "Do 200": 800 pcs/hr, margin 320%, test 10%.
        Satén: 20mm × 200m, 509 CZK ex-VAT (→ 615.89 incl).
        TTR: 69mm × 200m, 441 CZK ex-VAT (→ 533.61 incl).
        Global rate: 810 CZK/hr, tax 15%.
        """
        material = MaterialInput(
            purchase_price=509.0,
            purchase_vat_included=False,
            purchase_vat_pct=21.0,
            roll_width_mm=20.0,
            roll_length_m=200.0,
            material_type="roll",
            name="Satén bílá 20mm",
            addons=[
                AddonInput(
                    purchase_price=441.0,
                    purchase_vat_included=False,
                    purchase_vat_pct=21.0,
                    roll_width_mm=69.0,
                    roll_length_m=200.0,
                    color_name="Stříbrná",
                ),
            ],
        )
        tier = TierInput(
            pieces_per_hour=800,
            margin_pct=320,
            waste_test_pct=10,
            waste_pruning_pct=30,  # ignored for TTR
        )
        job = JobInput(width=20, height=40, quantity=10, production_type="thermotransfer")
        tax = TaxConfig(income_tax_rate=15, apply_material_grossup=True)

        result = calculate(job, material, tier, tax, hourly_rate=810)

        assert result.material_cost_raw == pytest.approx(0.306, abs=0.01)

    def test_satin_full_price_with_margin_and_labor(self) -> None:
        """Full TTR: material + margin + labor + rounding = 2.30 CZK."""
        material = MaterialInput(
            purchase_price=509.0,
            purchase_vat_included=False,
            purchase_vat_pct=21.0,
            roll_width_mm=20.0,
            roll_length_m=200.0,
            material_type="roll",
            name="Satén bílá 20mm",
            addons=[
                AddonInput(
                    purchase_price=441.0,
                    purchase_vat_included=False,
                    purchase_vat_pct=21.0,
                    roll_width_mm=69.0,
                    roll_length_m=200.0,
                    color_name="Stříbrná",
                ),
            ],
        )
        tier = TierInput(pieces_per_hour=800, margin_pct=320, waste_test_pct=10)
        job = JobInput(width=20, height=40, quantity=10, production_type="thermotransfer")
        tax = TaxConfig(income_tax_rate=15, apply_material_grossup=True)

        result = calculate(job, material, tier, tax, hourly_rate=810)

        # material_with_margin = ~0.306 × 4.2 ≈ 1.285
        # labor = 810/800 = 1.0125
        # raw ≈ 2.297 → ceil to 0.10 = 2.30
        assert result.unit_price == 2.30

    def test_leatherette_large_batch_cheaper(self) -> None:
        """500 pcs cheaper per unit than 10 pcs."""
        material = MaterialInput(
            purchase_price=310.0,
            purchase_vat_included=True,
            sheet_width=600.0,
            sheet_height=300.0,
            material_type="sheet",
            name="Koženka",
        )
        tier_small = TierInput(pieces_per_hour=80, margin_pct=320, waste_test_pct=10, waste_pruning_pct=15)
        tier_large = TierInput(pieces_per_hour=120, margin_pct=300, waste_test_pct=10, waste_pruning_pct=12)
        tax = TaxConfig(income_tax_rate=15, apply_material_grossup=True)

        r_small = calculate(
            JobInput(width=30, height=20, quantity=10, production_type="laser"),
            material,
            tier_small,
            tax,
            hourly_rate=810,
        )
        r_large = calculate(
            JobInput(width=30, height=20, quantity=500, production_type="laser"),
            material,
            tier_large,
            tax,
            hourly_rate=810,
        )
        assert r_large.unit_price < r_small.unit_price

    def test_leatherette_tier_brackets_decreasing(self) -> None:
        """Multiple tier brackets produce decreasing unit prices."""
        material = MaterialInput(
            purchase_price=310.0,
            purchase_vat_included=True,
            sheet_width=600.0,
            sheet_height=300.0,
            material_type="sheet",
            name="Koženka",
        )
        tax = TaxConfig(income_tax_rate=15, apply_material_grossup=True)

        brackets = [
            (TierInput(pieces_per_hour=80, margin_pct=320, waste_test_pct=10, waste_pruning_pct=15), 10),
            (TierInput(pieces_per_hour=100, margin_pct=310, waste_test_pct=10, waste_pruning_pct=15), 50),
            (TierInput(pieces_per_hour=120, margin_pct=300, waste_test_pct=10, waste_pruning_pct=12), 200),
            (TierInput(pieces_per_hour=150, margin_pct=280, waste_test_pct=8, waste_pruning_pct=10), 700),
            (TierInput(pieces_per_hour=200, margin_pct=260, waste_test_pct=8, waste_pruning_pct=10), 2000),
        ]
        prices = []
        for tier, qty in brackets:
            result = calculate(
                JobInput(width=30, height=20, quantity=qty, production_type="laser"),
                material,
                tier,
                tax,
                hourly_rate=810,
            )
            prices.append(result.unit_price)

        for i in range(1, len(prices)):
            assert prices[i] < prices[i - 1], f"Tier bracket {i} not cheaper than {i - 1}: {prices}"
