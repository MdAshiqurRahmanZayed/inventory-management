# Spec Delta

## Purpose

Lets a Manager or Stock User correct a product's recorded quantity at a location to match a physical count or write off damage/loss, with every correction fully audited through the same move/quant machinery as any other stock change.

## ADDED Requirements

### Requirement: Adjustment record
The system SHALL provide `im.adjustment` with: `product_id` (required, → `im.product`), `location_id` (required, → `im.location`, internal type only), `adjustment_type` (Increase/Decrease), `quantity` (required, > 0), `reason` (required, text), `user_id` (the creating user), and `date` (defaults to now).

#### Scenario: Create an adjustment
- **WHEN** a user creates an adjustment for a product at an internal location with a positive quantity and a reason
- **THEN** the adjustment is saved and available to confirm

#### Scenario: Reason is required
- **WHEN** a user tries to save an adjustment with no reason
- **THEN** the system rejects the save with a clear validation error

#### Scenario: Location restricted to internal locations
- **WHEN** a user opens the location field on an adjustment
- **THEN** only locations whose `type` is internal are selectable

### Requirement: Confirming an adjustment creates and completes a move
The system SHALL, when an adjustment is confirmed, create one `im.move` linked to it via `adjustment_id` and drive it immediately through Draft → Confirmed → Done: for an Increase, `source_id` empty and `dest_id` the adjustment's location; for a Decrease, `source_id` the adjustment's location and `dest_id` empty.

#### Scenario: Increase adjustment raises stock
- **WHEN** a user confirms an Increase adjustment of 5 units for a product at a location
- **THEN** a Done `im.move` is created linked to the adjustment, and the product's quant at that location increases by 5

#### Scenario: Decrease adjustment is rejected below zero
- **WHEN** a user confirms a Decrease adjustment whose quantity exceeds the product's quant at that location
- **THEN** the system rejects the confirmation with a clear validation error, consistent with the stock-floor rule enforced on every move

### Requirement: A confirmed adjustment is immutable
The system SHALL reject any edit to a confirmed adjustment's `product_id`, `location_id`, `adjustment_type`, or `quantity`, matching the immutability of the Done move it created.

#### Scenario: Editing a confirmed adjustment rejected
- **WHEN** a user tries to change the quantity on a confirmed adjustment
- **THEN** the system rejects the edit with a clear validation error
