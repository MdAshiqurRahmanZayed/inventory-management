## Context

Phase 1 left `im.warehouse`/`im.location` with no notion of a "default" receiving location, and `im.product.qty_on_hand` as an unused stored placeholder. See proposal.md for why purchasing needs to land now. This design covers the move state machine, the quant upsert mechanics, and how a purchase order resolves where receipts land.

## Goals / Non-Goals

**Goals:**
- A single, reusable move state machine and quant-update path that Phase 3 (sales/shipments/adjustments) can call into without changes.
- Stock quantities always traceable to a specific Done move — no code path writes `im.quant` except that one.

**Non-Goals:**
- Multi-step routing (e.g. putaway strategies, pick/pack/ship chains) — out of scope until a real need appears.
- Costing methods (FIFO/average) — `unit_cost` on a purchase line is informational only in this phase.
- Sales, shipments, adjustments, or any `im.move` source other than purchasing — Phase 3.

## Decisions

**State machine as a guarded `write()` override, not a workflow library.**
Odoo 19 has no built-in lightweight state-machine mixin worth adding as a dependency for four states. `im.move.write()` checks `state` transitions against an explicit allowed-transitions map (`{Draft: [Confirmed, Cancelled], Confirmed: [Done, Cancelled], Done: [], Cancelled: []}`) before calling `super().write()`, and raises `ValidationError` on an illegal jump. Editing any of `product_id`/`quantity`/`source_id`/`dest_id` on an already-Done record is blocked in the same override. Alternative considered: a separate `_check_transition` model constraint — rejected because `write()` is the only place that needs to see both old and new state together.

**Warehouse default receiving location: explicit flag, not "first internal location found".**
`im.location` gets a new boolean `is_default_receiving` (internal type only). `im.warehouse` gets a computed `default_receiving_location_id` that returns the one location where that flag is set, raising a clear error at confirm-time if none or more than one is flagged. Alternative considered: silently picking the first internal location by creation order — rejected as too implicit; a Manager should be able to see and change which location receipts land at.

**Quant upsert lives on `im.quant` as a classmethod-style helper (`_apply_move`), called only from `im.move`'s Done transition.**
`im.quant._apply_move(product, location, delta)` does a `search` for the existing `(product_id, location_id)` row; updates it if found, creates it if not. Called twice for a move with both source and dest (decrement source, increment dest), once for a receipt (dest only, since `source_id` is empty). Runs under `sudo()` internally, since the placeholder ACLs (`base.group_system`) would otherwise let any Manager write `im.quant` directly too — the guard is enforced in code, not by ACL, until Phase 4 introduces real per-model access rules.

**Direct `im.quant` writes blocked via an internal context flag, not by removing write access.**
`im.quant.create()`/`write()` raise unless `self.env.context.get("im_allow_quant_write")` is truthy; `_apply_move` sets that context before calling `create`/`write` on itself. This keeps the placeholder `base.group_system` ACL (needed so the read-only list view and future admin tooling work) while still stopping accidental direct edits from the UI or API. Phase 4's real access rules can eventually make this redundant, but removing it now isn't warranted for a placeholder-access phase.

**`qty_on_hand` becomes a non-stored computed field.**
`fields.Float(compute="_compute_qty_on_hand")` summing `im.quant` search results for the product, computed on read rather than stored+recomputed on every quant change. Simpler and correct by construction; the cost is that sorting/filtering the product list by `qty_on_hand` requires loading all products rather than an indexed query. Acceptable at this phase's data volumes (demo data, portfolio-scale) — revisit with `store=True` + `depends` if a later phase needs list-level performance.

**Purchase order confirm creates moves in a single transaction; no partial-confirm state.**
Confirming validates "has at least one line" first, then creates all receipt moves and flips `state` to Confirmed together. If move creation fails partway, the whole confirm rolls back (standard ORM transaction behavior) — there is no code path that leaves an order Confirmed with fewer moves than lines.

**Sequence-backed display names for `im.purchase.order` and `im.move`.**
`im.purchase.order.number` auto-generates via `ir.sequence` as "PO-0001", "PO-0002", etc.; the computed `name` field displays as "PO-0001 Supplier-Warehouse" (e.g., "PO-0001 Acme Corp-Main Warehouse"). Similarly, `im.move.number` generates as "SM-00001", and `name` displays as "SM-00001 Product xQty" (e.g., "SM-00001 Laptop x5"). Both sequences are noupdate=1 in demo data so they persist across module reinstalls. Rationale: tells the user a stable reference number plus context at a glance; replaces opaque "im.purchase.order,2" listings in dropdowns and list views.

## Risks / Trade-offs

- [Risk] Non-stored `qty_on_hand` could get slow if demo data grows much larger. → Mitigation: switch to stored+computed with `depends` on `im.quant` writes; no spec-level change needed since the requirement is the value, not the storage strategy.
- [Risk] Context-flag guard on `im.quant` is a soft guard (bypassable by anyone constructing the same context key). → Mitigation: acceptable for this phase given `base.group_system` is already a full-access placeholder for everything; Phase 4's real access rules are the actual hardening point, already tracked in the roadmap.
- [Risk] `default_receiving_location_id` erroring when zero/multiple locations are flagged could block confirming a purchase order on warehouses carried over from Phase 1 demo data that predate this flag. → Mitigation: demo data update in this change sets `is_default_receiving=True` on one location per existing demo warehouse.
