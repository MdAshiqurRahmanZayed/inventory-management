# Tasks

## 1. Dashboard data: stock value and low-stock

- [x] 1.1 Add stock-value aggregate to `get_dashboard_data()` (`sum(quantity * product.cost)` across `im.quant`, joined to `im.product`); verify with a test: known quant quantities and product costs produce the expected total, and zero quants produce 0.
- [x] 1.2 Add low-stock count to `get_dashboard_data()` (count of `im.alert` where `state = 'open'`); verify with a test: open vs. closed alerts are counted correctly.

## 2. Dashboard data: open orders and recent moves

- [x] 2.1 Add open-orders count to `get_dashboard_data()` (combined count of `im.purchase.order` and `im.sale.order` in `draft`/`confirmed`); verify with a test: done/cancelled orders are excluded.
- [x] 2.2 Add 7-day-moves count and origin breakdown (receipt/delivery/adjustment, inferred from `purchase_line_id`/`shipment_id`/`adjustment_id`) to `get_dashboard_data()`, filtered on `done_date` within the last 7 days; verify with a test: moves outside the window and non-Done moves are excluded, and the breakdown sums to the total.

## 3. Dashboard data: top movers

- [x] 3.1 Add top-5-movers aggregate to `get_dashboard_data()` (products ranked by summed `quantity` across Done moves in the last 30 days); verify with a test: ranking order is correct and fewer-than-5 active products doesn't pad the list.

## 4. Dashboard frontend

- [x] 4.1 Add stock-value and low-stock tiles to `dashboard.xml`/`.scss`, reading the new data fields; verify by loading the dashboard and confirming the tiles render with correct values against demo data.
- [x] 4.2 Add an open-orders tile; verify it renders alongside the existing tile row.
- [x] 4.3 Add a 7-day-moves chart (bar chart: receipt/delivery/adjustment counts) using the existing Chart.js bundle already loaded for the pie charts; verify it renders without JS console errors.
- [x] 4.4 Add a top-movers ranked list (product name + quantity moved); verify it renders the top 5 (or fewer) correctly.

## 5. PDF stock report

- [x] 5.1 Add `reports/im_stock_report.xml` with an `ir.actions.report` (qweb-pdf) and QWeb template scoped to one `im.warehouse`, listing product/SKU/quantity/value lines from `im.quant` filtered to that warehouse's `location_ids`, excluding zero-quantity lines, with a grand total; register in `__manifest__.py`; verify by generating a PDF from demo data and checking line contents and total against a manual calculation.
- [x] 5.2 Add a "Print Stock Report" button to `im_warehouse_views.xml`'s form view triggering the report for that record; verify clicking it from a warehouse form produces a PDF scoped to that warehouse.
- [x] 5.3 Add a test asserting the report's data-preparation method excludes zero-stock products and scopes correctly to one warehouse's locations (not relying on rendering the PDF itself, per standard Odoo report-testing practice of testing the data method directly).

## 6. Documentation

- [x] 6.1 Update README's Status line and Milestones/Phase 5 notes to reflect the completed widget set and report; verify by reading the rendered section for accuracy against what was actually built.
