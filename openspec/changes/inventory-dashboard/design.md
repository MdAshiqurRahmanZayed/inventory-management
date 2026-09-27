## Context

Builds on `phase-1-core-models` (products, categories, partner roles, warehouses, locations all exist and have demo data) and `initial-project-scaffold` (the `im.welcome` landing page it replaces). See proposal.md for motivation.

## Goals / Non-Goals

**Goals:**
- Replace the static welcome message with a real, data-backed dashboard.
- Keep it honest: only show metrics the current data model actually supports.
- Follow the plan doc's intent (an OWL frontend) without needing stock-move/order data that doesn't exist yet.

**Non-Goals:**
- Stock value, low-stock alerts, open orders, recent moves, top movers — plan doc's full dashboard scope, deferred until purchasing/sales/stock phases exist.
- Any new business fields on existing models — this change only reads data, doesn't add to it.
- Role-based dashboard content (Viewer vs Manager) — no role groups exist yet (Phase 4); the dashboard is visible to whoever can open the app (same access as today's landing page).

## Decisions

- **OWL client action, not a `qweb`/plain HTML report.** Matches the plan doc's explicit "OWL dashboard" architecture choice and is the standard modern Odoo pattern for this kind of page (same category of thing `web_responsive`'s pieces and Odoo's own apps use) — worth doing properly now rather than deferring the OWL setup cost to the later, more complex dashboard.
- **Charts via Odoo's already-bundled Chart.js (`web.chartjs_lib`), not a new dependency.** Odoo core ships Chart.js (`/web/static/lib/Chart/Chart.js`, used by graph views) — add `"web.chartjs_lib"` to the client action's owl bundle and render via a `<canvas>` ref in the OWL component, same pattern Odoo's own graph view uses. No new asset to vendor or CDN to load.
- **Data via a dedicated model method, not several small RPC calls from the frontend.** `im.dashboard.get_dashboard_data()` (a model with no persisted records, just a data-fetching entry point) returns one payload with all counts, the products-per-category breakdown, and the partner-role breakdown in a single call (two `read_group`s), called once via `orm.call`. Keeps the frontend simple and the query count low.
- **Remove `im.welcome` entirely, not keep it alongside.** It was an explicit scaffold placeholder (see `initial-project-scaffold`'s design.md) with no reason to keep once superseded; keeping both would leave two "landing page" concepts in the codebase.
- **No caching/polling.** Counts are cheap `read_group`/`search_count` queries at this data volume (demo data: dozens of records); refetch on every dashboard load, no need for real-time updates yet.

## Risks / Trade-offs

- [Dashboard becomes stale reference point once stock/order data exists] → Expected and fine: this dashboard is explicitly scoped to current data; the later stock/order phase's dashboard work extends or replaces these widgets, not this design.
- [OWL asset bundle adds a new manifest `assets` key, first JS/OWL in this module] → One-time setup cost; needed regardless for the plan doc's eventual full dashboard, so doing it now isn't wasted.

## Open Questions

None — scope, data source, and frontend approach above are final for this change.
