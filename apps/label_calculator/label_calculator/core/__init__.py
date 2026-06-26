"""Core calculation engine — pure Python, zero Frappe dependencies.

All business logic lives here so it can be tested without a running
Frappe instance (pytest -m unit).
"""

from label_calculator.core.calculator import LabelSpec, PriceResult, calculate_label_price
from label_calculator.core.default_data import load_default_data
from label_calculator.core.models import (
    AddonInput,
    CalcResult,
    JobInput,
    MachineInput,
    MaterialInput,
    MaterialMachineParams,
    TierInput,
)

__all__ = [
    "AddonInput",
    "CalcResult",
    "JobInput",
    "LabelSpec",
    "MaterialInput",
    "MaterialMachineParams",
    "MachineInput",
    "PriceResult",
    "TierInput",
    "calculate_label_price",
    "load_default_data",
]
