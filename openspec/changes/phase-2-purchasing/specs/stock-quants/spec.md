## Purpose

Tracks current stock per product per location as a derived total, so the rest of the system has one place to read "how much is here" without recomputing from move history each time.

## ADDED Requirements

### Requirement: Quant record
The system SHALL provide `im.quant` with: `product_id` (required, → `im.product`), `location_id` (required, → `im.location`), and `quantity` (float, default 0.0), with at most one quant row per `product_id`/`location_id` pair.

#### Scenario: First stock at a location creates a quant
- **WHEN** a product has never had stock at a given location and a move to that location reaches Done
- **THEN** a new `im.quant` row is created for that product/location pair with the moved quantity

#### Scenario: Subsequent moves update the same quant
- **WHEN** a product already has a quant at a location and another move to that location reaches Done
- **THEN** the existing quant row's quantity is updated, not a duplicate row created

### Requirement: Quants are not directly editable
The system SHALL only allow `im.quant` quantities to change as a side effect of an `im.move` reaching Done, not through direct user create/write on the model.

#### Scenario: Direct edit blocked
- **WHEN** a user without elevated/system access tries to write to an `im.quant` record directly
- **THEN** the system rejects the write

### Requirement: Quants are viewable
The system SHALL provide a read-only list view of `im.quant`, reachable from a menu under Inventory Management, showing product, location, and quantity.

#### Scenario: Browse current stock
- **WHEN** a user opens the Stock Quants menu
- **THEN** they see every product/location pair that has ever had stock, with its current quantity
