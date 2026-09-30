## Why

Phase 1 gave the module products, partners, warehouses and locations, but no way to actually bring stock in. `qty_on_hand` on `im.product` is still a static placeholder field nobody writes to. This change adds purchasing — the supplier side of the plan doc's ER diagram — so buying from a supplier creates real, auditable stock: `im.purchase.order`, `im.purchase.line`, the `im.move` state machine (Draft → Confirmed → Done), and `im.quant` as the per-location running total. Sales, shipments and manual adjustments are deliberately out of scope here (Phase 3); this change only needs the receipt side of `im.move` to exist.

## What Changes

- Add `im.purchase.order`: `supplier_id` (domain-restricted to Supplier/Both partners), `order_date`, `expected_date`, `state` (Draft/Confirmed/Done/Cancelled), `amount_total` (computed from lines).
- Add `im.purchase.line`: `order_id`, `product_id`, `quantity`, `unit_cost`, `subtotal` (computed).
- Add `im.move`: `product_id`, `quantity`, `source_id`, `dest_id` (both `im.location`, source nullable for a receipt from an external supplier), `state` (Draft/Confirmed/Done/Cancelled), `done_date`, `user_id`, `purchase_line_id` (nullable — only receipt moves set this in this change; `shipment_id`/`adjustment_id` are added in Phase 3, not here).
- Add `im.quant`: `product_id`, `location_id`, `quantity` — one row per product/location pair, written only when a move transitions to Done.
- Purchase order lifecycle: confirming a Draft `im.purchase.order` creates one Draft `im.move` per line (dest = the warehouse's default internal location, source = none). Setting an order to Done requires all its moves to be Done.
- Move lifecycle: Draft → Confirmed → Done is a guarded transition (no skipping states, no editing a Done move). Setting a move to Done upserts the destination `im.quant` (and decrements the source quant when one is set) and stamps `done_date`/`user_id`.
- Stock floor: a move that would take an internal location's quant below zero is rejected. Receipt moves in this change always have quantity > 0 and no internal source, so the floor check exists here as the shared guard future phases (sales, transfers) reuse.
- `qty_on_hand` on `im.product` becomes a computed field (sum of that product's `im.quant` rows) instead of the Phase 1 placeholder stored float.
- List/form views + menus for `im.purchase.order` (with an editable one2many for lines) and `im.move`; `im.quant` gets a read-only list view (no manual create/edit — enforced in the view and at the access-control layer).
- Access: continue the Phase 1 placeholder pattern (`base.group_system`, full R/W/C/D) for the three new models — real Viewer/User/Manager rules land in Phase 4 as already noted in Phase 1.
- Demo data: a handful of purchase orders (mix of Draft/Confirmed/Done) against the existing demo suppliers and products, so Done ones populate real `im.quant` rows and the dashboard's future stock-value widget has something to show.
- Tests (`TransactionCase`): order confirm creates correct moves, move state guards (no skip, no edit after Done), quant math after a Done move (including a second Done move accumulating correctly), negative-stock rejection, `qty_on_hand` computes from quants.

## Capabilities

### New Capabilities
- `purchasing`: Purchase orders and lines can be created and confirmed against a supplier, driving receipt stock moves.
- `stock-moves`: Stock moves carry a guarded Draft→Confirmed→Done state machine and are the only path by which stock quantities change.
- `stock-quants`: Per-product, per-location stock totals are tracked and kept in sync exclusively by moves reaching Done.

### Modified Capabilities
- `product-catalog`: `im.product.qty_on_hand` changes from a stored placeholder float to a computed field summed from `im.quant`.

## Impact

- New files under `addons/inventory_management/`: `models/im_purchase_order.py`, `models/im_purchase_line.py`, `models/im_move.py`, `models/im_quant.py`, matching `views/*.xml`, updated `security/ir.model.access.csv`, `demo/*.xml`, `tests/*.py`.
- Modified: `models/im_product.py` (`qty_on_hand` becomes computed), `models/im_warehouse.py` (needs a way to resolve a "default internal location" for receipts — likely a computed/stored field or a simple lookup method), `__manifest__.py` (new data/demo file lists).
- No change to the dashboard, MCP connector, or sales/adjustment flows — those stay out of scope until Phase 3.
