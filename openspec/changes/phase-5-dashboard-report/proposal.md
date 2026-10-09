# Proposal

## Why

The dashboard currently shows only 6 record counts and 2 pie charts (products by category, partners by role) — numbers that don't need Phase 2/3's purchase/sale/move data to compute. Now that purchasing, sales, shipments, moves, and low-stock alerts are real, the dashboard can show what the README promised from the start: stock value, what's low, what's open, recent activity, and what's moving fastest. The PDF stock report per warehouse is the other README v1 commitment that hasn't landed yet.

## What Changes

- Add five dashboard widgets to `im.dashboard.get_dashboard_data()` and the OWL frontend:
  - **Stock value**: total value on hand (`sum(im.quant.quantity * im.product.cost)` across all locations).
  - **Low-stock count**: count of open `im.alert` records (reuses Phase 4's alert model, not a fresh reorder-level scan).
  - **Open orders**: count of `im.purchase.order` and `im.sale.order` records in `draft` or `confirmed` state.
  - **7-day moves**: count of `im.move` records with `done_date` in the last 7 days, plus a small trend breakdown (receipts vs. deliveries vs. adjustments).
  - **Top movers**: the 5 products with the highest total quantity moved (sum of `im.move.quantity` for Done moves) in the last 30 days.
- Add a PDF report, "Stock Report," generated per warehouse: product, SKU, on-hand quantity, and value, for every product with stock in that warehouse's locations, with a grand total. Triggered from the warehouse form/list (Manager and above, matching warehouse access).
- Access for all of the above follows existing role access: widgets show only data each viewer already has read access to (Viewer sees counts/values the way Viewer already can see `im.quant`/`im.move`/orders; the PDF report option is visible per the `im.warehouse` access level, i.e. Manager-only generation, though the report's own read is bounded by normal model access regardless).

## Capabilities

### New Capabilities
- `dashboard-widgets`: the five new OWL dashboard tiles/charts and their backing `im.dashboard` data method, built from Phase 2-4 data.
- `stock-report`: the per-warehouse PDF stock report (QWeb report + trigger action).

### Modified Capabilities
(none — no capability specs have been archived yet; the existing 6-count/2-chart dashboard was built before this project adopted per-capability specs, so there's nothing under `openspec/specs/` to delta against)

## Impact

- `addons/inventory_management/models/im_dashboard.py` — extend `get_dashboard_data()` with the five new aggregates.
- `addons/inventory_management/static/src/dashboard/dashboard.js` / `.xml` / `.scss` — new widget markup, a bar/line chart for 7-day moves, a ranked list for top movers.
- `addons/inventory_management/reports/` — new QWeb report template + `ir.actions.report` record for the per-warehouse PDF.
- `addons/inventory_management/views/im_warehouse_views.xml` — add a "Print Stock Report" button.
- `addons/inventory_management/tests/` — new tests for the dashboard data method's aggregates and the report's data selection (per-warehouse scoping, zero-stock exclusion).
- `addons/inventory_management/__manifest__.py` — register the new report file(s).
