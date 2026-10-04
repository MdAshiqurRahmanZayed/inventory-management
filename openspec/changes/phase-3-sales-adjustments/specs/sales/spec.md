# Spec Delta

## Purpose

Lets a Manager or Stock User sell products to a customer, turning a sale order into an outgoing shipment and the stock-decreasing moves that go with it once confirmed.

## ADDED Requirements

### Requirement: Sale order record
The system SHALL provide `im.sale.order` with: `customer_id` (required, → `res.partner`, domain restricted to Customer/Both), `warehouse_id` (required, → `im.warehouse`, the shipping warehouse), `order_date`, `expected_date`, `state` (Draft/Confirmed/Done/Cancelled, default Draft), and `amount_total` (computed from its lines).

#### Scenario: Create a sale order
- **WHEN** a user creates a sale order against a customer contact
- **THEN** the order is saved in Draft state with `amount_total` 0

#### Scenario: Customer field restricted to customers
- **WHEN** a user opens the customer field on a sale order
- **THEN** only contacts whose `partner_role` is Customer or Both are selectable

### Requirement: Sale order line
The system SHALL provide `im.sale.line` with: `order_id` (required, → `im.sale.order`), `product_id` (required, → `im.product`), `quantity` (required, > 0), `unit_price`, and `subtotal` (computed as `quantity * unit_price`).

#### Scenario: Add a line to a draft order
- **WHEN** a user adds a line for a product with quantity 10 and unit price 8.0
- **THEN** the line's subtotal is 80.0 and the order's `amount_total` updates to include it

#### Scenario: Zero or negative quantity rejected
- **WHEN** a user tries to save a sale line with quantity 0 or less
- **THEN** the system rejects the save with a clear validation error

### Requirement: Confirming an order creates a shipment and delivery moves
The system SHALL, when a Draft sale order is confirmed, create one `im.shipment` and one Draft `im.move` per order line: `product_id` and `quantity` from the line, `source_id` the order's warehouse default shipping location, `dest_id` empty (external customer), and `shipment_id` set to the created shipment.

#### Scenario: Confirm a draft order
- **WHEN** a Manager confirms a Draft sale order with two lines
- **THEN** the order moves to Confirmed state, one `im.shipment` is created, and two Draft `im.move` records exist, one per line, each linked to that shipment

#### Scenario: Confirming an order with no lines is rejected
- **WHEN** a user tries to confirm a sale order that has no lines
- **THEN** the system rejects the confirmation with a clear validation error

#### Scenario: Confirming is rejected when stock would go negative
- **WHEN** a Manager confirms a sale order whose line quantity exceeds the product's `qty_on_hand` at the shipping location
- **THEN** the system still creates the Draft moves, but delivering them (transitioning to Done) is rejected until enough stock is available, consistent with the stock-floor rule enforced on every move

### Requirement: Shipment record
The system SHALL provide `im.shipment` with: `sale_order_id` (required, → `im.sale.order`), `warehouse_id`, `shipment_date`, and `status` (Draft/Confirmed/Done/Cancelled, default Draft) that tracks the aggregate state of its linked moves.

#### Scenario: Shipment created by order confirmation
- **WHEN** a sale order is confirmed
- **THEN** its shipment is created in Draft status with the order's warehouse

### Requirement: Delivering all pending moves in one step
The system SHALL provide an action that, for a Confirmed shipment, transitions every one of its linked `im.move` records still in Draft or Confirmed straight through to Done, applying each move's normal state-machine and stock-quant effects.

#### Scenario: Deliver all pending moves
- **WHEN** a user triggers "deliver all" on a Confirmed shipment with two Draft moves and sufficient stock
- **THEN** both moves become Done and their source quants decrease accordingly

### Requirement: Shipment and order reach Done only when all moves are Done
The system SHALL only allow a Confirmed shipment (and its sale order) to be marked Done once every one of the shipment's linked `im.move` records is Done.

#### Scenario: Order held at Confirmed until delivery completes
- **WHEN** a Confirmed shipment has one Done move and one Confirmed move
- **THEN** the shipment and its sale order cannot be set to Done, and the system reports why

#### Scenario: Order completes once all moves are done
- **WHEN** every move linked to a Confirmed shipment reaches Done
- **THEN** the shipment and its sale order can be marked Done
