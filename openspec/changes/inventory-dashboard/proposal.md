## Why

The app's landing page is currently a static `im.welcome` message ("scaffolded and running, no business features yet"). With Phase 1's data model in place (products, categories, partners, warehouses, locations), the app can show a real dashboard instead — giving reviewers and users something to actually look at on login, ahead of orders/moves/the full plan-doc dashboard (which needs stock-move data that doesn't exist yet).

## What Changes

- Replace the `im.welcome` landing page/action with a real OWL dashboard client action, scoped to what current data can support:
  - Product count, category count
  - Warehouse count, location count
  - Supplier count, customer count (from `res.partner`)
  - **Pie chart**: products per category
  - **Pie chart**: partner role split (Supplier / Customer / Both)
- Remove `im.welcome` (model, view, access row) — superseded by the dashboard.
- No stock-value, low-stock, open-orders, or recent-moves widgets yet — those need purchase/sales/stock-move data from later changes; explicitly out of scope here rather than faked with placeholder numbers.

## Capabilities

### New Capabilities
- `inventory-dashboard`: An OWL-based dashboard landing page showing counts and pie-chart breakdowns (products by category, partners by role) from the current product/partner/warehouse/location data.

### Modified Capabilities
(none — `im.welcome` was scaffolding, not a documented capability with its own spec)

## Impact

- New files under `addons/inventory_management/`: `models/im_dashboard.py` (data-fetching methods), `static/src/dashboard/*` (OWL component, template, styling), updated `views/inventory_management_menu.xml` (new client action), updated `__manifest__.py` (`assets` bundle).
- Removed: `models/im_welcome.py`, its view/menu wiring, its `ir.model.access.csv` row.
- No change to `im.product`, `im.product.category`, `im.warehouse`, `im.location`, or `res.partner` — the dashboard only reads existing data, no new fields.
