## Purpose

Lets a Manager or Stock User buy products from a supplier, turning a purchase order into real incoming stock once confirmed.

## ADDED Requirements

### Requirement: Purchase order record
The system SHALL provide `im.purchase.order` with: `supplier_id` (required, → `res.partner`, domain restricted to Supplier/Both), `warehouse_id` (required, → `im.warehouse`, the receiving warehouse), `order_date`, `expected_date`, `state` (Draft/Confirmed/Done/Cancelled, default Draft), and `amount_total` (computed from its lines).

#### Scenario: Create a purchase order
- **WHEN** a user creates a purchase order against a supplier contact
- **THEN** the order is saved in Draft state with `amount_total` 0

#### Scenario: Supplier field restricted to suppliers
- **WHEN** a user opens the supplier field on a purchase order
- **THEN** only contacts whose `partner_role` is Supplier or Both are selectable

### Requirement: Purchase order line
The system SHALL provide `im.purchase.line` with: `order_id` (required, → `im.purchase.order`), `product_id` (required, → `im.product`), `quantity` (required, > 0), `unit_cost`, and `subtotal` (computed as `quantity * unit_cost`).

#### Scenario: Add a line to a draft order
- **WHEN** a user adds a line for a product with quantity 10 and unit cost 5.0
- **THEN** the line's subtotal is 50.0 and the order's `amount_total` updates to include it

#### Scenario: Zero or negative quantity rejected
- **WHEN** a user tries to save a purchase line with quantity 0 or less
- **THEN** the system rejects the save with a clear validation error

### Requirement: Confirming an order creates receipt moves
The system SHALL, when a Draft purchase order is confirmed, create one Draft `im.move` per order line: `product_id` and `quantity` from the line, `source_id` empty (external supplier), `dest_id` the order's warehouse default internal location, and `purchase_line_id` set to that line.

#### Scenario: Confirm a draft order
- **WHEN** a Manager confirms a Draft purchase order with two lines
- **THEN** the order moves to Confirmed state and two Draft `im.move` records exist, one per line, each linked to its originating line

#### Scenario: Confirming an order with no lines is rejected
- **WHEN** a user tries to confirm a purchase order that has no lines
- **THEN** the system rejects the confirmation with a clear validation error

### Requirement: Receiving all pending moves in one step
The system SHALL provide an action that, for a Confirmed purchase order, transitions every one of its linked `im.move` records still in Draft or Confirmed straight through to Done, applying each move's normal state-machine and stock-quant effects.

#### Scenario: Receive all pending moves
- **WHEN** a user triggers "receive all" on a Confirmed purchase order with two Draft moves
- **THEN** both moves become Done and their destination quants update accordingly

### Requirement: Order reaches Done only when its moves are Done
The system SHALL only allow a Confirmed purchase order to be marked Done once every one of its linked `im.move` records is Done.

#### Scenario: Order held at Confirmed until receipt completes
- **WHEN** a Confirmed purchase order has one Done move and one Confirmed move
- **THEN** the order cannot be set to Done, and the system reports why

#### Scenario: Order completes once all moves are done
- **WHEN** every move linked to a Confirmed purchase order reaches Done
- **THEN** the order can be marked Done
