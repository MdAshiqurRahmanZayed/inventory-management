## 1. Locations & warehouse default receiving location

- [x] 1.1 Add `is_default_receiving` boolean to `im_location.py` (internal locations only)
- [x] 1.2 Add `default_receiving_location_id` computed field to `im_warehouse.py`, raising a clear error if zero or more than one internal location is flagged
- [x] 1.3 Update `im_location_views.xml`/`im_warehouse_views.xml` to show the new flag

## 2. Stock moves

- [x] 2.1 Create `models/im_move.py` (`im.move`: `product_id`, `quantity`, `source_id`, `dest_id`, `state`, `done_date`, `user_id`, `purchase_line_id`)
- [x] 2.2 Add constraint: at least one of `source_id`/`dest_id` required
- [x] 2.3 Implement guarded state transitions in `write()` (Draft→Confirmed→Done, any non-Done→Cancelled; reject skipped/backward transitions)
- [x] 2.4 Block edits to `product_id`/`quantity`/`source_id`/`dest_id` once `state` is Done
- [x] 2.5 On transition to Done: call `im.quant._apply_move` for dest (increment) and source (decrement) as applicable, stamp `done_date`/`user_id`

## 3. Stock quants

- [x] 3.1 Create `models/im_quant.py` (`im.quant`: `product_id`, `location_id`, `quantity`), unique constraint on `(product_id, location_id)`
- [x] 3.2 Implement `_apply_move(product, location, delta)` upsert helper, run under `sudo()`
- [x] 3.3 Guard `create()`/`write()` to reject unless called via the internal `im_allow_quant_write` context flag
- [x] 3.4 Implement stock-floor check: reject a Done transition that would take an internal location's quant below zero

## 4. Product catalog: computed qty_on_hand

- [x] 4.1 Change `im.product.qty_on_hand` from stored placeholder float to non-stored `compute="_compute_qty_on_hand"`, summing `im.quant` rows for that product across all locations

## 5. Purchasing

- [x] 5.1 Create `models/im_purchase_order.py` (`im.purchase.order`: `supplier_id` domain-restricted to Supplier/Both, `warehouse_id`, `order_date`, `expected_date`, `state`, `amount_total` computed)
- [x] 5.2 Create `models/im_purchase_line.py` (`im.purchase.line`: `order_id`, `product_id`, `quantity` > 0, `unit_cost`, `subtotal` computed)
- [x] 5.3 Implement order confirm action: validate at least one line, create one Draft `im.move` per line (source empty, dest = warehouse's `default_receiving_location_id`, `purchase_line_id` set), flip order to Confirmed
- [x] 5.4 Implement order Done guard: only allowed once every linked move is Done
- [x] 5.5 Add `state`-transition validation to the order model consistent with move's pattern (no skipping Draft→Done)
- [x] 5.6 Implement `action_receive_all`: for a Confirmed order, transitions each Draft/Confirmed linked move through to Done

## 6. Security & manifest

- [x] 6.1 Add `ir.model.access.csv` rows for `im.purchase.order`, `im.purchase.line`, `im.move`, `im.quant` (`base.group_system`, placeholder full R/W/C/D, per Phase 1 pattern — replaced in Phase 4)
- [x] 6.2 Update `__manifest__.py`: new `data` (views, security) and `demo` file entries

## 7. Views

- [x] 7.1 List/form views + menu for `im.purchase.order`, with an editable one2many for lines on the form, and a Confirm/Done button respecting the state guards
- [x] 7.2 List/form views + menu for `im.move`, showing state and linked purchase line
- [x] 7.3 Read-only list view + menu for `im.quant` (no create/edit affordances in the view)

## 8. Demo data

- [x] 8.1 Set `is_default_receiving=True` on one location per existing demo warehouse
- [x] 8.2 Add demo purchase orders (mix of Draft/Confirmed/Done) against existing demo suppliers/products, so Done ones populate real `im.quant` rows

## 9. Tests

- [x] 9.1 `TransactionCase`: confirming an order creates correct moves (right product/quantity/dest/purchase_line_id per line)
- [x] 9.2 `TransactionCase`: move state guards — skipping a state rejected, editing a Done move rejected
- [x] 9.3 `TransactionCase`: quant math after a Done move, and after a second Done move accumulating on the same product/location
- [x] 9.4 `TransactionCase`: negative-stock rejection on an internal location
- [x] 9.5 `TransactionCase`: direct `im.quant` create/write without the internal context flag is rejected
- [x] 9.6 `TransactionCase`: `qty_on_hand` computes correctly from quants across multiple locations, and is 0 with none
- [x] 9.7 `TransactionCase`: purchase order Done guard — blocked while any linked move isn't Done, allowed once all are

## 10. Verification

- [x] 10.1 Rebuild/upgrade `inventory_management` in local Docker Odoo; fresh install with `--with-demo` loads with 0 errors
- [x] 10.2 Manually browse: create a purchase order, confirm it, set its moves to Done, confirm the product's `qty_on_hand` and the Quants list reflect it
- [x] 10.3 Run tests isolated to this module (`--test-tags /inventory_management --stop-after-init`): 0 failed, 0 errors
