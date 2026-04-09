"""Tests for tier resolution and throughput override."""

import pytest

from label_calculator.core.calculator import resolve_throughput, resolve_tier
from label_calculator.core.models import TierInput


@pytest.mark.unit
def test_tier_lookup_bracket_match() -> None:
    """resolve_tier matches quantity within min/max bracket."""
    tier = TierInput(pieces_per_hour=80, margin_pct=320, min_quantity=1, max_quantity=29)
    result = resolve_tier([tier], 10)
    assert result is not None
    assert result.pieces_per_hour == 80


@pytest.mark.unit
def test_tier_lookup_empty_returns_none() -> None:
    """Empty tier list returns None."""
    result = resolve_tier([], 50)
    assert result is None


@pytest.mark.unit
def test_tier_lookup_out_of_range_returns_none() -> None:
    """Quantity outside all brackets returns None."""
    tier = TierInput(pieces_per_hour=80, margin_pct=320, min_quantity=1, max_quantity=29)
    result = resolve_tier([tier], 100)
    assert result is None


@pytest.mark.unit
def test_tier_override_replaces_throughput() -> None:
    """Override replaces tier's pieces_per_hour."""
    tier = TierInput(pieces_per_hour=80, margin_pct=320)
    throughput = resolve_throughput(tier, override_pcs_per_hour=600)
    assert throughput == 600


@pytest.mark.unit
def test_tier_no_override_uses_default() -> None:
    """Without override, tier's pieces_per_hour is used."""
    tier = TierInput(pieces_per_hour=80, margin_pct=320)
    throughput = resolve_throughput(tier, override_pcs_per_hour=None)
    assert throughput == 80


@pytest.mark.unit
def test_vip_profile_different_tiers() -> None:
    """VIP tiers (lower margin) vs standard (higher margin)."""
    standard = TierInput(pieces_per_hour=80, margin_pct=320)
    vip = TierInput(pieces_per_hour=80, margin_pct=200)
    assert vip.margin_pct < standard.margin_pct
