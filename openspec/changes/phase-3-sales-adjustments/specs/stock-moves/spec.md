# Spec Delta

## MODIFIED Requirements

### Requirement: Move record
The system SHALL provide `im.move` with: `product_id` (required, → `im.product`), `quantity` (required, > 0), `source_id` (→ `im.location`, nullable), `dest_id` (→ `im.location`, nullable), `state` (Draft/Confirmed/Done/Cancelled, default Draft), `done_date`, `user_id`, `purchase_line_id` (→ `im.purchase.line`, nullable), `shipment_id` (→ `im.shipment`, nullable), and `adjustment_id` (→ `im.adjustment`, nullable).

#### Scenario: Move requires at least one location
- **WHEN** a move is created with both `source_id` and `dest_id` empty
- **THEN** the system rejects the save with a clear validation error

#### Scenario: A move traces to at most one originating document
- **WHEN** a move is created with more than one of `purchase_line_id`, `shipment_id`, or `adjustment_id` set
- **THEN** the system rejects the save with a clear validation error
