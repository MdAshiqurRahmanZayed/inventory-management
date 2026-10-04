# Tasks

## 1. Locations & warehouse default shipping location

- [x] 1.1 Add `is_default_shipping` boolean to `im_location.py` (internal locations only), mirroring `is_default_receiving`'s constraint
- [x] 1.2 Add `default_shipping_location_id` computed field (or `_get_default_shipping_location()` method, matching the existing receiving pattern) to `im_warehouse.py`, raising a clear error if zero or more than one internal location is flagged
- [x] 1.3 Update `im_location_views.xml`/`im_warehouse_views.xml` to show the new flag

## 2. Stock moves: new origin fields

- [x] 2.1 Add `shipment_id` (→ `im.shipment`, nullable) and `adjustment_id` (→ `im.adjustment`, nullable) fields to `im_move.py`
- [x] 2.2 Add `_check_single_origin` constraint: reject a move with more than one of `purchase_line_id`/`shipment_id`/`adjustment_id` set, verified by a test
- [x] 2.3 Update `im_move_views.xml` to show shipment/adjustment links alongside the existing purchase line link

## 3. Sales

- [x] 3.1 Create `models/im_sale_order.py` (`im.sale.order`: `customer_id` domain-restricted to Customer/Both, `warehouse_id`, `order_date`, `expected_date`, `state`, `amount_total` computed)
- [x] 3.2 Create `models/im_sale_line.py` (`im.sale.line`: `order_id`, `product_id`, `quantity` > 0, `unit_price`, `subtotal` computed)
- [x] 3.3 Create `models/im_shipment.py` (`im.shipment`: `sale_order_id`, `warehouse_id`, `shipment_date`, `status`)
- [x] 3.4 Implement order confirm action: validate at least one line, create one `im.shipment`, create one Draft `im.move` per line (source = warehouse's default shipping location, dest empty, `shipment_id` set), flip order to Confirmed
- [x] 3.5 Implement shipment/order Done guard: only allowed once every linked move is Done
- [x] 3.6 Add `state`-transition validation to the order and shipment models consistent with move's pattern (no skipping Draft→Done)
- [x] 3.7 Implement `action_deliver_all`: for a Confirmed shipment, transitions each Draft/Confirmed linked move through to Done
- [x] 3.8 Add sequence-backed `number`/`name` (computed) fields to `im.sale.order` and `im.shipment`, matching Phase 2's purchase order/move naming pattern; add `ir.sequence` records to `data/ir_sequence.xml`

## 4. Adjustments

- [x] 4.1 Create `models/im_adjustment.py` (`im.adjustment`: `product_id`, `location_id` domain-restricted to internal, `adjustment_type` Increase/Decrease, `quantity` > 0, `reason` required, `user_id`, `date`)
- [x] 4.2 Implement confirm action: create one `im.move` linked via `adjustment_id` (Increase: dest = location, source empty; Decrease: source = location, dest empty) and drive it Draft → Confirmed → Done in the same call
- [x] 4.3 Block edits to a confirmed adjustment's `product_id`/`location_id`/`adjustment_type`/`quantity`, matching the Done move's immutability

## 5. Security & manifest

- [x] 5.1 Add `ir.model.access.csv` rows for `im.sale.order`, `im.sale.line`, `im.shipment`, `im.adjustment` (`base.group_system`, placeholder full R/W/C/D, per Phase 1-2 pattern — replaced in Phase 4)
- [x] 5.2 Update `__manifest__.py`: new `data` (views, security) and `demo` file entries

## 6. Views

- [x] 6.1 List/form views + menu for `im.sale.order`, with an editable one2many for lines on the form, and a Confirm/Done button respecting the state guards
- [x] 6.2 List/form views + menu for `im.shipment`, showing status and linked moves, with a "Deliver all" button
- [x] 6.3 Form view + menu for `im.adjustment`, with a Confirm button; list view showing type/quantity/reason/user/date as an audit trail

## 7. Demo data

- [x] 7.1 Set `is_default_shipping=True` on one location per existing demo warehouse
- [x] 7.2 Add demo sale orders (mix of Draft/Confirmed/Done) against existing demo customers/products with enough prior stock (from Phase 2's Done purchase orders) to deliver successfully
- [x] 7.3 Add one or two demo adjustments (one Increase, one Decrease) showing a populated audit trail

## 8. Tests

- [x] 8.1 `TransactionCase`: confirming a sale order creates a shipment and correct moves (right product/quantity/source/shipment_id per line)
- [x] 8.2 `TransactionCase`: sale/shipment Done guard — blocked while any linked move isn't Done, allowed once all are
- [x] 8.3 `TransactionCase`: delivering would take stock negative is rejected at the move's Done transition
- [x] 8.4 `TransactionCase`: `_check_single_origin` rejects a move with more than one origin FK set
- [x] 8.5 `TransactionCase`: Increase adjustment raises `qty_on_hand`/quant correctly; Decrease adjustment below available stock is rejected
- [x] 8.6 `TransactionCase`: editing a confirmed adjustment is rejected

## 9. Verification

- [x] 9.1 Rebuild/upgrade `inventory_management` in local Docker Odoo; fresh install with `--with-demo` loads with 0 errors
- [ ] 9.2 Manually browse: create a sale order, confirm it, deliver its shipment, confirm the product's `qty_on_hand` decreases and the Quants list reflects it; create and confirm an adjustment and confirm the same
- [x] 9.3 Run tests isolated to this module (`--test-tags /inventory_management --stop-after-init`): 0 failed, 0 errors
