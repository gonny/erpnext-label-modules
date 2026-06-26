# Manual testing scenarios for the Label Calculator in ERPNext 16

This guide uses the standard ERPNext 16 Desk workflow described in the ERPNext User Manual and Frappe Framework navigation docs:

1. Sign in to ERPNext Desk.
2. Use the module/DocType menu or the `/` global search to open the calculator entry in your local installation.
3. Click New to open a blank form.
4. Enter the values below and save the document.
5. Verify that the calculated result fields and the generated description match the expected output.

If your local installation exposes the calculator through a custom DocType or a custom module page, use the same field values below and verify the same result values in the form.

The expected values below were computed from the current pure-Python engine in `apps/label_calculator/label_calculator/core/calculator.py` and the default seed data in `apps/label_calculator/label_calculator/fixtures/default_data.json`.

## Scenario 1: Laser label, small batch

Use this scenario to confirm that a basic laser calculation returns the expected unit and total price.

- UI path: Desk → search/open the calculator entry → New → fill the form → Save
- Material: `Bílý vinyl 305x610mm`
- Production type: `laser`
- Width (mm): `50`
- Height (mm): `50`
- Quantity: `100`
- Price ex VAT: `45.00`
- VAT rate: `21`
- Hourly rate: `20`
- Pieces per hour: `150`
- Margin (%): `50`
- Waste test pieces: `5`
- Waste test (%): `15`
- Waste pruning (%): `12`
- Sheet width (mm): `305`
- Sheet height (mm): `610`
- Material type: `sheet`
- Cut margin (%): `8`

Expected output:
- Unit price: `2.10 CZK`
- Total price: `210.00 CZK`
- Currency: `CZK`
- Description line: `Bílý vinyl 305x610mm 50mm x 50mm, laser`

## Scenario 2: Laser label, larger batch

Use this scenario to confirm that a larger batch uses the updated tier-style inputs and still produces a stable result.

- UI path: Desk → search/open the calculator entry → New → fill the form → Save
- Material: `Bílý vinyl 305x610mm`
- Production type: `laser`
- Width (mm): `60`
- Height (mm): `40`
- Quantity: `300`
- Price ex VAT: `45.00`
- VAT rate: `21`
- Hourly rate: `20`
- Pieces per hour: `800`
- Margin (%): `25`
- Waste test pieces: `2`
- Waste test (%): `8`
- Waste pruning (%): `8`
- Sheet width (mm): `305`
- Sheet height (mm): `610`
- Material type: `sheet`
- Cut margin (%): `8`

Expected output:
- Unit price: `1.40 CZK`
- Total price: `420.00 CZK`
- Currency: `CZK`
- Description line: `Bílý vinyl 305x610mm 60mm x 40mm, laser`

## Scenario 3: Thermotransfer ribbon, price-floor check

Use this scenario to confirm that a thermotransfer calculation uses the ribbon-length path and respects the minimum unit price floor.

- UI path: Desk → search/open the calculator entry → New → fill the form → Save
- Material: `Saténová stuha bílá 25mm`
- Production type: `thermotransfer`
- Width (mm): `20`
- Height (mm): `20`
- Quantity: `100`
- Price ex VAT: `0.80`
- VAT rate: `21`
- Hourly rate: `100`
- Pieces per hour: `100`
- Margin (%): `80`
- Waste test pieces: `0`
- Waste test (%): `0`
- Waste pruning (%): `0`
- Sheet width (mm): `25`
- Sheet height (mm): `100000`
- Material type: `roll`
- Cut margin (%): `0`

Expected output:
- Unit price: `1.041 CZK`
- Total price: `104.10 CZK`
- Currency: `CZK`
- Description line: `Saténová stuha bílá 25mm 20mm x 20mm, standard tisk`
