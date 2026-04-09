import frappe
from frappe.model.document import Document


class LabelPricingProfile(Document):
    """Customer pricing policy. At most one profile can have is_default=True."""

    def validate(self) -> None:
        self._validate_single_default()

    def _validate_single_default(self) -> None:
        if self.is_default:
            existing = frappe.db.exists(
                "Label Pricing Profile",
                {"is_default": 1, "name": ("!=", self.name)},
            )
            if existing:
                frappe.throw("Only one pricing profile can be the default.")
