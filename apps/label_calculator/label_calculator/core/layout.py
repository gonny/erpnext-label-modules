"""Sheet/roll nesting and waste computation — pure Python, zero Frappe imports."""

from __future__ import annotations

import math

from label_calculator.core.models import TierInput


def sheet_layout(sheet_w: float, sheet_h: float, label_w: float, label_h: float, kerf: float = 0.0) -> int:
    """Compute how many labels fit on one sheet, trying both orientations.

    Kerf reduces usable area per label (effective size = label + kerf).

    Args:
        sheet_w: Sheet width in mm.
        sheet_h: Sheet height in mm.
        label_w: Label width in mm.
        label_h: Label height in mm.
        kerf: Kerf width in mm (0 for TTR printers).

    Returns:
        Maximum number of labels per sheet (at least 1).
    """
    if label_w <= 0 or label_h <= 0:
        raise ValueError("Label dimensions must be positive")
    if sheet_w <= 0 or sheet_h <= 0:
        raise ValueError("Sheet dimensions must be positive")

    eff_w = label_w + kerf
    eff_h = label_h + kerf

    # Orientation A: label as-is
    across_a = math.floor(sheet_w / eff_w)
    down_a = math.floor(sheet_h / eff_h)
    count_a = across_a * down_a

    # Orientation B: label rotated 90°
    across_b = math.floor(sheet_w / eff_h)
    down_b = math.floor(sheet_h / eff_w)
    count_b = across_b * down_b

    return max(count_a, count_b, 1)


def roll_layout(roll_width: float, segment_length: float, label_w: float, label_h: float, kerf: float = 0.0) -> int:
    """Compute labels per roll segment.

    For rolls, width = roll width, segment_length = roll length or segment.

    Args:
        roll_width: Roll width in mm.
        segment_length: Roll length (or segment) in mm.
        label_w: Label width in mm.
        label_h: Label height in mm.
        kerf: Kerf width in mm.

    Returns:
        Number of labels per roll segment (at least 1).
    """
    return sheet_layout(roll_width, segment_length, label_w, label_h, kerf)


def compute_effective_quantity(quantity: int, tier: TierInput) -> int:
    """Compute actual quantity needed including all waste components.

    Formula: quantity + test_pieces + ceil(qty × test%) + ceil(qty × pruning%)

    Args:
        quantity: Desired label quantity.
        tier: Tier with waste parameters.

    Returns:
        Effective quantity including waste.
    """
    test_pieces = tier.waste_test_pieces
    test_pct_waste = math.ceil(quantity * tier.waste_test_pct / 100)
    pruning_waste = math.ceil(quantity * tier.waste_pruning_pct / 100)
    return quantity + test_pieces + test_pct_waste + pruning_waste
