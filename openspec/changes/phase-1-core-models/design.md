## Context

Builds directly on `initial-project-scaffold` (module installs, Docker env works, `im.*` naming convention established, `im.welcome` landing page exists). See proposal.md for motivation. No role groups (Viewer/User/Manager) exist yet — that's Phase 4 per the README's Milestones table — so access control here is intentionally coarse.

## Goals / Non-Goals

**Goals:**
- A correct, minimal data model for products, partner roles, warehouses, and locations that later phases (purchasing, sales, stock, dashboard) build on without needing schema changes.
- Real demo data so the app looks populated on first install (per plan doc's testing section: ~20 products, 5 suppliers, 10 customers, 2 warehouses).
- Basic `TransactionCase` tests proving the models behave.

**Non-Goals:**
- No purchase/sales orders, no stock moves, no `im.quant` computation — `qty_on_hand` is a placeholder field only.
- No real role-based access (Viewer/User/Manager) — Phase 4's job. Using a single coarse access level for now.
- No OWL dashboard, no MCP connector.

## Decisions

- **`im.product.category` as its own model, not `res.partner.category`-style tags.** Matches the plan doc's explicit scope ("Product categories as their own model").
- **`uom` as a plain text field, not Odoo's `uom.uom` model.** Full unit-of-measure conversion (e.g. boxes ↔ units) is out of scope for v1 per the plan doc; a text field avoids pulling in `uom` module complexity for a field that's just descriptive at this stage. Revisit only if a later phase needs real UoM conversion math.
- **`res.partner` extended via inheritance (`_inherit`), not a new model.** Plan doc explicitly calls for reusing Odoo's own contacts; matches the ER diagram (`RES_PARTNER` is Odoo core, not `im.*`).
- **`partner_role` as a stored selection field; `is_supplier`/`is_customer` as stored computed fields (not just `@api.depends` non-stored).** They need to be usable in view domains (e.g. filtering the product form's supplier field) and search filters — non-stored computed fields can't be searched/filtered directly in Odoo without extra `search=` methods, so storing them is simpler and matches the plan doc's explicit mention of "used to filter order forms."
- **`im.location.type`** as a plain selection (internal/vendor/customer) — matches the ER diagram exactly, no separate model needed for location types.
- **Access rows: `base.group_system` (Settings/Administration) as a placeholder**, not `base.group_user`, so this phase's data isn't accidentally readable/writable by every future non-privileged demo user before Phase 4 defines real Stock Viewer/User/Manager groups. This is a deliberately temporary, coarse choice — Phase 4 replaces these rows entirely.
- **Demo data via a `demo/` XML file** referenced in `__manifest__.py`'s `demo` list (not `data`), so it only loads when demo data is enabled — matches how the earlier `docker compose`/install verification already works without demo data by default.

## Risks / Trade-offs

- [Coarse `base.group_system` access is wrong long-term] → Explicitly temporary and documented; Phase 4 fully replaces `ir.model.access.csv` rows for these models with real Viewer/User/Manager rows.
- [`uom` as text now might need migration to `uom.uom` later if real conversion is needed] → Accepted per plan doc's stated v1 scope (no complex UoM math needed); flag as a note for the v2 roadmap if it comes up.
- [`qty_on_hand` placeholder field could be mistaken for real stock data] → Field is default 0.0 and unused by any view logic yet; will be redefined as a computed field (from `im.quant`) in the stock phase without a data migration, since the field name doesn't change.

## Open Questions

None — scope, models, and field choices above are final for this change.
