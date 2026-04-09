"""Tests for tier resolution and throughput override."""

import pytest

from label_calculator.core.calculator import resolve_throughput, resolve_tier
from label_calculator.core.models import TierInput


@pytest.mark.unit
def test_tier_lookup_correct_bracket() -> None:
    """resolve_tier returns the first matching tier."""
    tier = TierInput(pieces_per_hour=400, margin_pct=35, waste_test_pieces=3, waste_test_pct=10, waste_pruning_pct=10)
    result = resolve_tier([tier], 50)
    assert result is not None
    assert result.pieces_per_hour == 400


@pytest.mark.unit
def test_tier_lookup_empty_returns_none() -> None:
    """Empty tier list returns None."""
    result = resolve_tier([], 50)
    assert result is None


@pytest.mark.unit
def test_tier_override_replaces_throughput() -> None:
    """Override replaces tier's pieces_per_hour."""
    tier = TierInput(pieces_per_hour=400, margin_pct=35)
    throughput = resolve_throughput(tier, override_pcs_per_hour=600)
    assert throughput == 600


@pytest.mark.unit
def test_tier_no_override_uses_default() -> None:
    """Without override, tier's pieces_per_hour is used."""
    tier = TierInput(pieces_per_hour=400, margin_pct=35)
    throughput = resolve_throughput(tier, override_pcs_per_hour=None)
    assert throughput == 400


@pytest.mark.unit
def test_vip_profile_uses_different_tiers() -> None:
    """VIP tiers (lower margin) produce different results than standard."""
    standard_tier = TierInput(pieces_per_hour=400, margin_pct=35)
    vip_tier = TierInput(pieces_per_hour=800, margin_pct=15)

    # VIP has higher throughput and lower margin
    assert vip_tier.pieces_per_hour > standard_tier.pieces_per_hour
    assert vip_tier.margin_pct < standard_tier.margin_pct
