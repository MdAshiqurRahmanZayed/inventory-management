# Design

## Context

See proposal.md - Why. Current `im.dashboard.get_dashboard_data()` (`models/im_dashboard.py`) returns 6 counts and 2 `_read_group` breakdowns; the OWL component (`static/src/dashboard/dashboard.js`/`.xml`) renders them as tiles + Chart.js pies under `o_im_dashboard_tiles`/`o_im_dashboard_charts`. `im.move` has no direct "origin type" field — its type is inferred from which of `purchase_line_id` / `shipment_id` / `adjustment_id` is set (`models/im_move.py:47-49`), exactly one non-false per the `_check_single_origin` constraint. `im.warehouse` already has `location_ids` (one2many) and existing helpers for default receiving/shipping locations (`models/im_warehouse.py`) — the report's per-warehouse scoping follows the same `location_ids` relation. No `reports/` directory or `ir.actions.report` exists yet in this module.

## Goals / Non-Goals

**Goals:**
- Extend `get_dashboard_data()` with the five new aggregates, each a single additional `_read_group`/`search_count`/`search` call — no new stored/computed fields needed on existing models.
- Add one new QWeb report (`ir.actions.report`, `report_type: qweb-pdf`) scoped by `active_id` to one `im.warehouse`.
- Keep every widget computed from the requesting user's own `self.env` (no `sudo()`), so widget data is automatically bounded by that user's existing model access — no new access rules needed for the dashboard itself.

**Non-Goals:**
- No new stored fields, no schema migration. Every widget is a read-time aggregate over existing data.
- No drill-down/click-through from a widget into its underlying records (e.g., clicking the low-stock tile doesn't navigate to the alert list) — out of scope for this phase, matching the existing dashboard's tiles which are also non-interactive.
- No date-range picker for the 7-day/30-day windows; they're fixed, matching the README's own phrasing ("moves in the last 7 days").
- No multi-warehouse comparison report — one PDF, one warehouse, matching the README's "PDF stock report per warehouse."

## Decisions

**Stock value and top-movers computed in Python, not SQL views.** `im.quant` and `im.move` are small tables for this project's scale (demo data: ~20 products, a few warehouses); a `_read_group`/`search` plus a Python-side `sum()`/sort is simpler than introducing a SQL view or `read_group` with computed aggregates, and keeps the whole data method readable in one place. Alternative considered: a stored `total_value` field on a singleton config-like model, updated via write overrides on `im.quant` — rejected as premature optimization and extra invalidation surface for a number that only needs to be fresh when the dashboard loads.

**7-day-moves breakdown by origin uses the existing exactly-one-of-three-fields constraint, not a new `move_type` field.** `_check_single_origin` (`models/im_move.py:51-59`) already guarantees a Done move has exactly one of `purchase_line_id` (receipt), `shipment_id` (delivery), or neither (which combined with `adjustment_id` set means adjustment) set. The breakdown groups on which field is set rather than adding a stored `move_type` selection field, since the existing fields are already the source of truth and a new field would just duplicate it.

**Open-orders count is`im.purchase.order` + `im.sale.order` combined**, matching the proposal's single "Open Orders" tile (not two separate tiles), since the dashboard's existing tile row is already fairly wide (6 tiles) and the two order types are conceptually "things still in flight" from one glance.

**PDF report built as a standard QWeb report (`ir.actions.report`) triggered by a button on `im.warehouse`'s form view**, not a wizard. The report needs no user input beyond "which warehouse" — that's already the record the button lives on — so a wizard would add a step with nothing to configure. Alternative considered: a wizard offering a warehouse picker from any screen — rejected since the warehouse form/list is already the natural place to print a report about that warehouse, per the requirement "triggered from the warehouse record."

**Report query reuses `im.quant`, filtered by `location_id in warehouse.location_ids`,** joined to `im.product` for name/SKU/cost — no new computed field on `im.warehouse` for "total stock value," since the report needs line-level detail anyway and the grand total is just `sum(line values)` computed in the report's Python prep method.

## Risks / Trade-offs

- [Computing stock value and top-movers in Python on every dashboard load could get slow as data grows] → Acceptable for this project's stated scale (demo data for a resume/portfolio piece, not a production deployment per README's own "not production-ready" status); if it ever matters, the aggregates can move to stored computed fields later without changing the dashboard's external contract (`get_dashboard_data()`'s return shape stays the same).
- [7-day/30-day windows are server-clock-relative (`fields.Datetime.now() - timedelta(...)`), so a demo installed at different times shows different "last 7 days" results] → Expected and correct behavior for a live dashboard; not a bug, just means screenshots taken at different times won't match demo data exactly, which is already true of the existing dashboard's counts.
- [A product with stock split across many lots/locations within one warehouse could make the report long] → Out of scope to paginate or summarize further; the README's own scope already excludes lots/serials (v2 roadmap), so one line per product per warehouse (aggregated across that warehouse's locations) is the right level of detail for v1.

## Migration Plan

1. Extend `im_dashboard.py`'s `get_dashboard_data()` with the five new aggregates; this is additive to the returned dict, so no frontend change is required to land it first (tested independently).
2. Update the OWL dashboard (`dashboard.js`/`.xml`/`.scss`) to render the five new widgets, reading from the already-extended data method.
3. Add the QWeb report (template + `ir.actions.report` + manifest registration) and the warehouse form button, independent of steps 1-2.
4. Tests land alongside each step's own code (dashboard aggregate tests with step 1, report tests with step 3), not deferred to a final step.

## Open Questions

(none — scope and approach above are settled; nothing here would change the specs or task breakdown if decided later)
