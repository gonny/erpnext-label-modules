from frappe.model.document import Document

from label_calculator.core.machine import compute_hourly_rate


class LabelMachine(Document):
    """Thin controller that delegates hourly rate computation to core."""

    def validate(self) -> None:
        self._compute_hourly_rate()

    def _compute_hourly_rate(self) -> None:
        if self.lifetime_hours and self.lifetime_hours > 0:
            self.hourly_rate = compute_hourly_rate(
                purchase_price=float(self.purchase_price or 0),
                lifetime_hrs=float(self.lifetime_hours),
                maintenance_annual=float(self.maintenance_annual or 0),
                energy_cost_per_hr=float(self.energy_cost_per_hr or 0),
                working_hrs_per_year=float(self.working_hours_per_year or 2000),
            )
