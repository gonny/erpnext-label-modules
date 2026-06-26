"""Focused unit tests for the pure-Python label pricing engine."""

import pytest

from label_calculator.core.calculator import LabelSpec, PriceResult, calculate_label_price
from label_calculator.core.default_data import load_default_data


@pytest.mark.unit
def test_calculate_label_price_returns_price_result(sample_label_spec: LabelSpec) -> None:
    """calculate_label_price should return a PriceResult for valid input."""
    result = calculate_label_price(sample_label_spec)
    assert isinstance(result, PriceResult)


@pytest.mark.unit
def test_calculate_label_price_total_equals_unit_times_quantity(sample_label_spec: LabelSpec) -> None:
    """Total price must equal unit_price x quantity (within float rounding)."""
    result = calculate_label_price(sample_label_spec)
    expected_total = round(result.unit_price * sample_label_spec.quantity, 2)
    assert result.total_price == expected_total


@pytest.mark.unit
def test_calculate_label_price_minimum_unit_price() -> None:
    """Very small labels should still get a minimum unit price of 1.0."""
    tiny_spec = LabelSpec(width_mm=1.0, height_mm=1.0, quantity=100)
    result = calculate_label_price(tiny_spec)
    assert result.unit_price >= 1.0


@pytest.mark.unit
def test_calculate_label_price_currency_is_czk(sample_label_spec: LabelSpec) -> None:
    """Default currency for all calculations is CZK."""
    result = calculate_label_price(sample_label_spec)
    assert result.currency == "CZK"


@pytest.mark.unit
def test_load_default_data_contains_seed_materials() -> None:
    """The bundled fixture should contain the default material groups and sample materials."""
    data = load_default_data()
    assert data["material_groups"][0]["name"] == "Saténové stuhy"
    assert data["materials"][1]["name"] == "Bily vinyl 305x610mm"
    assert data["pricing_profiles"][0]["code"] == "standard"
