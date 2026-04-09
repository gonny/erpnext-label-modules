"""Frappe hooks for the label_calculator app."""

app_name = "label_calculator"
app_title = "Label Calculator"
app_publisher = "Label Calculator Contributors"
app_description = "Label price calculator for self-adhesive labels, integrated with ERPNext sales workflow."
app_email = ""
app_license = "MIT"

# ─── DocType overrides ───────────────────────────────────────────────────────
# override_doctype_class = {}

# ─── Document Events ─────────────────────────────────────────────────────────
# doc_events = {}

# ─── Scheduled Tasks ─────────────────────────────────────────────────────────
# scheduler_events = {}

# ─── Fixtures ────────────────────────────────────────────────────────────────
fixtures = [
    "Label Material Group",
    "Label Material",
    "Label Machine",
    "Label Material Machine Params",
    "Label Pricing Profile",
    "Label Production Tier",
    "Label Material Tier Override",
    "Label Calculator Settings",
    {
        "dt": "Custom Field",
        "filters": [
            [
                "name",
                "in",
                [
                    "Quotation Item-label_width_mm",
                    "Quotation Item-label_height_mm",
                    "Quotation Item-label_material",
                    "Quotation Item-label_addon",
                    "Quotation Item-label_description",
                    "Sales Invoice Item-label_width_mm",
                    "Sales Invoice Item-label_height_mm",
                    "Sales Invoice Item-label_material",
                    "Sales Invoice Item-label_addon",
                    "Sales Invoice Item-label_description",
                ],
            ],
        ],
    },
]
