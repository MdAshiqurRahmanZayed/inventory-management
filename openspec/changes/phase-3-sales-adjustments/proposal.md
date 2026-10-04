# Proposal

## Why

Phase 2 gave the module a way to bring stock in (purchasing) but no way to sell it back out or correct it when a manual count disagrees with the system. Without sales and adjustments, `qty_on_hand` only ever goes up, and there's no audited path for the stock-floor corrections a warehouse inevitably needs (damage, loss, recount). Phase 3 closes that loop, reusing Phase 2's move/quant plumbing unchanged.

## What Changes

- Add `im.sale.order` / `im.sale.line`, mirroring the purchase order/line pattern (customer-facing instead of supplier-facing).
- Add `im.shipment`: confirming a sale order creates one shipment and one Draft `im.move` per line, sourced from the order's warehouse default *shipping* location (new `is_default_shipping` flag on `im.location`, parallel to Phase 2's `is_default_receiving`).
- Add an `im.adjustment` wizard + record: a Manager/User corrects a product's quantity at a location with a reason, which creates and immediately drives a single `im.move` through the existing state machine so the correction is fully audited.
- `im.move` gains `shipment_id` (→ `im.shipment`) and `adjustment_id` (→ `im.adjustment`) so every move traces back to exactly one originating document (purchase line, shipment, or adjustment).
- Sequence-backed display names for `im.sale.order` and `im.shipment`, matching Phase 2's `im.purchase.order`/`im.move` naming (e.g. "SO-0001 Customer-Warehouse").

**Not breaking**: no existing field, requirement, or behavior from Phase 1/2 changes meaning; this only adds new optional FKs and new models.

## Capabilities

### New Capabilities
- `sales`: Sale orders and lines; confirming a sale order creates a shipment and delivery moves against the order's warehouse.
- `adjustments`: Manual, audited stock corrections that go through the same move/quant machinery as every other stock change.

### Modified Capabilities
- `stock-moves`: `im.move`'s record requirement gains `shipment_id` (→ `im.shipment`, nullable) and `adjustment_id` (→ `im.adjustment`, nullable), alongside the existing `purchase_line_id`, so a move always traces to at most one originating document.

## Impact

- New models: `im.sale.order`, `im.sale.line`, `im.shipment`, `im.adjustment`.
- Modified models: `im.move` (two new nullable FKs), `im.location` (new `is_default_shipping` boolean + constraint mirroring `is_default_receiving`), `im.warehouse` (new `_get_default_shipping_location()` mirroring the receiving lookup).
- New views, menu items, demo data, and tests for all of the above, following the Phase 2 file layout under `addons/inventory_management/`.
- Access rows follow the Phase 1/2 placeholder pattern (`base.group_system`, full CRUD) — real role-based access is still Phase 4.
- No change to `im.quant`, `im.product`, or the move state machine itself.
