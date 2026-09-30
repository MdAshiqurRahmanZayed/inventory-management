## Purpose

Provides the single guarded path by which stock quantities ever change, so every quantity change has a traceable state transition and cannot be edited after the fact.

## ADDED Requirements

### Requirement: Move record
The system SHALL provide `im.move` with: `product_id` (required, → `im.product`), `quantity` (required, > 0), `source_id` (→ `im.location`, nullable), `dest_id` (→ `im.location`, nullable), `state` (Draft/Confirmed/Done/Cancelled, default Draft), `done_date`, `user_id`, and `purchase_line_id` (→ `im.purchase.line`, nullable).

#### Scenario: Move requires at least one location
- **WHEN** a move is created with both `source_id` and `dest_id` empty
- **THEN** the system rejects the save with a clear validation error

### Requirement: Move state machine
The system SHALL only allow a move to transition Draft → Confirmed → Done, or any non-Done state → Cancelled. Skipping a state (e.g. Draft directly to Done) SHALL be rejected.

#### Scenario: Sequential transition allowed
- **WHEN** a Draft move is confirmed, then the Confirmed move is set to Done
- **THEN** both transitions succeed

#### Scenario: Skipping a state rejected
- **WHEN** a user tries to set a Draft move directly to Done
- **THEN** the system rejects the transition with a clear validation error

### Requirement: A Done move is immutable
The system SHALL reject any edit to a move's `product_id`, `quantity`, `source_id`, or `dest_id` once its `state` is Done.

#### Scenario: Editing a done move rejected
- **WHEN** a user tries to change the quantity on a Done move
- **THEN** the system rejects the edit with a clear validation error

### Requirement: Done transition updates stock and stamps metadata
The system SHALL, when a move transitions to Done, update `im.quant` for its `dest_id` (increment by `quantity`) and its `source_id` (decrement by `quantity`) as applicable, and set `done_date` and `user_id` on the move.

#### Scenario: Receipt move increments destination quant
- **WHEN** a Confirmed move with no source and `dest_id` a warehouse location for 10 units of a product is set to Done
- **THEN** that product's quant at that location increases by 10, and the move's `done_date`/`user_id` are set

### Requirement: Stock floor enforced on internal locations
The system SHALL reject a Done transition that would leave an internal `im.location`'s quant for a product below zero.

#### Scenario: Move rejected when it would go negative
- **WHEN** a move would decrement an internal location's quant for a product below zero
- **THEN** the system rejects the Done transition with a clear validation error
