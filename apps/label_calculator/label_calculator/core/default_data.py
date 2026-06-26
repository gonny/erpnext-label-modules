"""Helpers for loading the app's default seed data."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_default_data() -> dict[str, Any]:
    """Load the bundled default data fixture for label pricing."""
    fixture_path = Path(__file__).resolve().parent / ".." / "fixtures" / "default_data.json"
    with fixture_path.open(encoding="utf-8") as handle:
        return json.load(handle)
