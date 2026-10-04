## Context

Phase 2 built the only state machine and quant-update path the system has (`im.move` + `im.quant._apply_move`), driven so far by purchasing alone. Phase 3 adds two more producers of moves — sales (via shipments) and manual adjustments — without touching that machine. See proposal.md for why both land together now.

## Goals / Non-Goals

**Goals:**
- Sales and adjustments both create and drive `im.move` records through the exact same `write()`-guarded state machine Phase 2 shipped; zero changes to `im.move.write()`, `im.quant._apply_move()`, or the stock-floor check.
- A move's origin is always unambiguous: exactly one of `purchase_line_id` / `shipment_id` / `adjustment_id` is set, never more than one.

**Non-Goals:**
- Partial shipments/deliveries (splitting one sale line across multiple shipments) — out of scope; one sale order confirmation produces exactly one shipment, as purchasing does today with its implicit "one order, N receipt moves" model.
- Reservations/backorders for insufficient stock — a sale order confirms and creates Draft moves regardless of current `qty_on_hand`; the existing stock-floor check on the Done transition is the only gate, exactly as it already behaves for purchasing's hypothetical over-ambitious receipts (not actually possible there since receipts only add stock, but the mechanism is shared).
- Costing/revenue recognition, invoicing — `unit_price` on a sale line is informational only, matching `unit_cost` on a purchase line.

## Decisions

**Shipment is a thin status wrapper around its moves, not a new state machine.**
`im.shipment.status` is a plain Selection field, set explicitly by code (not computed), updated in lockstep with its moves by the same `action_deliver_all`/`write()` pattern Phase 2 used for purchase orders. Alternative considered: compute `status` from the aggregate of linked moves — rejected for the same reason Phase 2's purchase order doesn't do this either: explicit state keeps the "only Done once all moves Done" guard a single `write()` check instead of a derived-field edge case.

**Default shipping location: new flag on `im.location`, parallel structure to `is_default_receiving`.**
`is_default_receiving` and the new `is_default_shipping` are independent booleans — a location can be both, one, or neither. `im.warehouse._get_default_shipping_location()` mirrors `_get_default_receiving_location()` exactly (same "exactly one flagged, internal-only" validation). Alternative considered: a single `receiving_or_shipping` selection field instead of two booleans — rejected because a small warehouse plausibly uses the same dock for both, which two independent booleans allow and a mutually-exclusive selection would not.

**"At most one origin" enforced as a `_check_single_origin` constraint on `im.move`, not a SQL check constraint.**
A Python `@api.constrains("purchase_line_id", "shipment_id", "adjustment_id")` counts how many are set and rejects if more than one. Alternative considered: a `CHECK` constraint at the DB level — rejected as unnecessary ceremony for a three-column mutual-exclusion rule only ever set by this module's own code paths (no direct SQL writes), consistent with how Phase 2 already enforces its invariants in Python, not SQL, everywhere else.

**Adjustment is a regular model with a Confirm action, not a `TransientModel` wizard.**
Despite the proposal's "wizard" framing (matching the README's original vocabulary), `im.adjustment` is implemented as a persisted model exactly like purchase/sale orders — confirming it creates and completes a move in one step (no separate Draft/Confirmed/Done lifecycle of its own; the adjustment itself is just Draft until confirmed, then immutable). Alternative considered: a true `TransientModel` wizard that disappears after use — rejected because the spec (and the README's "stored audit trail" requirement) needs the adjustment record to persist and be queryable after the fact, which a `TransientModel` does not reliably guarantee (rows are periodically garbage-collected by Odoo).

**Adjustment drives its move straight to Done in one transaction, no separate Draft/Confirmed step.**
Unlike purchase/sale orders (which create Draft moves a user later progresses), confirming an adjustment calls `create()` then `write({"state": "confirmed"})` then `write({"state": "done"})` on its move in the same method — there is no business reason to leave a manual correction half-applied. Alternative considered: Draft adjustment move requiring a separate "apply" step — rejected as needless friction for what is already a deliberate, reason-logged action.

## Risks / Trade-offs

- [Risk] A sale order can be confirmed (creating Draft moves) even when stock is already insufficient, only failing later at delivery time. → Mitigation: this matches the existing Phase 2 UX pattern (confirm now, fail at Done if invalid) rather than introducing a new validation path; acceptable since the error surfaces before any stock actually moves.
- [Risk] Two independent location flags (`is_default_receiving`, `is_default_shipping`) could both end up unset on a warehouse carried over from Phase 1/2 demo data, blocking sale order confirmation the same way Phase 2 risked blocking purchase confirmation. → Mitigation: demo data update in this change sets `is_default_shipping=True` on one location per existing demo warehouse, same fix Phase 2 applied for receiving.
- [Risk] The `_check_single_origin` constraint only guards this module's own create/write paths; nothing stops a future Phase from adding a fourth origin FK without updating the constraint. → Mitigation: acceptable now; the constraint's field list is a one-line edit when that happens, not a design that needs to anticipate it today.
