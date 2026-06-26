"""Layout helpers used by the pure-Python calculator."""

from __future__ import annotations

import math

from label_calculator.core.models import TierInput


def sheet_layout(sheet_w: float, sheet_h: float, label_w: float, label_h: float) -> int:
    """Estimate how many labels fit on a single sheet."""
    if sheet_w <= 0 or sheet_h <= 0 or label_w <= 0 or label_h <= 0:
        raise ValueError("All dimensions must be positive")

    across = math.floor(sheet_w / label_w)
    down = math.floor(sheet_h / label_h)
    return max(across * down, 1)


def roll_layout(roll_width: float, segment_length: float, label_w: float, label_h: float) -> int:
    """Estimate how many labels fit on a single roll segment."""
    if roll_width <= 0 or segment_length <= 0 or label_w <= 0 or label_h <= 0:
        raise ValueError("All dimensions must be positive")

    across = math.floor(roll_width / label_w)
    down = math.floor(segment_length / label_h)
    return max(across * down, 1)


def compute_effective_quantity(quantity: int, tier: TierInput) -> int:
    """Apply test/setup waste to the requested quantity."""
    if quantity <= 0:
        raise ValueError("Quantity must be positive")

    extra_test = math.ceil(quantity * (tier.waste_test_pct / 100))
    return quantity + tier.waste_test_pieces + extra_test
