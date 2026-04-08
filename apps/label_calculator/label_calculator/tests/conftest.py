"""Pytest configuration and shared fixtures for label_calculator tests."""

import pytest


@pytest.fixture
def sample_label_spec():
    """Return a basic LabelSpec for use in unit tests."""
    from label_calculator.core.calculator import LabelSpec

    return LabelSpec(width_mm=100.0, height_mm=50.0, quantity=1000, material_code="PAPER_MATTE")
