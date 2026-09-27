## 1. Backend data method

- [x] 1.1 Create `models/im_dashboard.py`: a model with no persisted fields, exposing `get_dashboard_data()` returning product count, category count, warehouse count, location count, supplier count, customer count, products-per-category breakdown, and partner-role breakdown (via `read_group`, two groupings)
- [x] 1.2 Add `ir.model.access.csv` row for `im.dashboard` (read-only, `base.group_user`)

## 2. OWL dashboard component

- [x] 2.1 Create `static/src/dashboard/dashboard.js`: OWL component, calls `get_dashboard_data()` on mount via `orm.call`; on render, instantiates two `Chart` (Chart.js) pie charts against `<canvas>` refs — one for products-per-category, one for partner-role split
- [x] 2.2 Create `static/src/dashboard/dashboard.xml`: template — stat tiles for the 6 counts, two `<canvas>` elements (one per pie chart) with labels
- [x] 2.3 Create `static/src/dashboard/dashboard.scss`: minimal styling for the tiles/chart layout
- [x] 2.4 Register the component as a client action (`registry.category("actions").add(...)`)
- [x] 2.5 Update `__manifest__.py`: add `assets` key registering the new JS/XML/CSS in `web.assets_backend` (`web.chartjs_lib` is loaded dynamically at runtime via `loadBundle`, not statically declared — matches Odoo core's own graph-view pattern)

## 3. Wire up as the landing page

- [x] 3.1 Update `views/inventory_management_menu.xml`: replace the `im.welcome` `ir.actions.act_window` with an `ir.actions.client` pointing at the new dashboard action tag
- [x] 3.2 Remove `models/im_welcome.py`, its `models/__init__.py` import line, and its `ir.model.access.csv` row

## 4. Verification

- [x] 4.1 Upgraded `inventory_management` in the local Docker Odoo. As with the earlier landing-page change, the action's underlying model changed (`ir.actions.act_window` → `ir.actions.client`), which Odoo won't let an XML upgrade morph in place — dropped and recreated `inventory_dev` fresh with `--with-demo`, confirmed 0 errors
- [x] 4.2 Manually opened the app in the browser: dashboard loads, all 6 counts match demo data exactly (20 products, 3 categories, 2 warehouses, 4 locations, 5 suppliers, 11 customer-flagged partners — 10 pure customers + 1 dual-role "Both"); both pie charts render correctly with legends (Electronics/Office Supplies/Furniture; Both/Customer/Supplier)
- [x] 4.3 Confirmed via network tab: `web.chartjs_lib` bundle and `get_dashboard_data` call both returned 200; no error dialog on final load

### Bugs found and fixed during verification
- `get_dashboard_data` wasn't decorated `@api.model`. Odoo's RPC dispatcher (`service/model.py`) unconditionally treats a non-`@api.model` method's first arg as a record-id list (`ids, args = args[0], args[1:]`); calling it with an empty `args` array from the frontend raised `IndexError: list index out of range` server-side (surfaced as an OWL lifecycle error client-side). Fixed by adding `@api.model` so the dispatcher skips the ids-extraction path entirely (matches how `@api.model`-decorated methods are dispatched per `get_public_method`).
- Chart.js with `maintainAspectRatio: false` needs an explicit-height container — without one the canvas grows unbounded downward each render, pushing the chart out of view. Fixed by wrapping each `<canvas>` in a dedicated `.o_im_dashboard_chart_canvas` div with a fixed height, separate from the chart's `<h4>` title (which needed to keep its natural height).
