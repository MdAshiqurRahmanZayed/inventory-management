# Stock Report

A per-warehouse PDF snapshot of what's actually on hand — useful for a physical audit, handing to an accountant, or just a clean export without opening Odoo.

## Generating one

**Inventory > Warehouses**, open the warehouse you want a report for. In the form's top action bar, click the **print icon** and choose **Stock Report** from the dropdown (exactly where every other Odoo document's "Print" action lives — if you've printed an invoice or a quotation in any Odoo app before, it's the same spot).

## What's in it

- One line per product currently in stock at that warehouse (any of its locations) — **product, SKU, quantity, value**.
- Products with **zero** quantity-on-hand at that warehouse are left out entirely — the report is "what's here," not a full product catalog with zeroes padded in.
- A grand total at the bottom, summing value across every line.

## Reading it

The report is scoped to **one warehouse only** — stock sitting at a different warehouse never appears, even for the same product. If you need a company-wide total, you'd generate one report per warehouse and add the grand totals yourself; there's no combined multi-warehouse report.

## Troubleshooting

**"The report is empty / says no stock."** Either nothing's been received into this warehouse yet, or everything that was here has since been delivered/adjusted out to zero. Check the warehouse's locations under its own form (the "Locations" tab) to confirm you're looking at the right one.

**"A product I know is in stock isn't showing up."** Double check it's actually at *this* warehouse's locations, not a different one — the report won't include stock elsewhere even if the product exists.
