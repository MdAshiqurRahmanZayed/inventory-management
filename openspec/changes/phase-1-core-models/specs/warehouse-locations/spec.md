## Purpose

Defines the physical structure — warehouses and the locations inside them — that stock will later be tracked against, before any stock-move logic exists.

## ADDED Requirements

### Requirement: Warehouse record
The system SHALL provide `im.warehouse` with `name` (required), `address`, `capacity` (float), and `email`.

#### Scenario: Create a warehouse
- **WHEN** a Manager creates a warehouse with a name and address
- **THEN** it is saved and appears in the warehouse list

### Requirement: Location belongs to a warehouse
The system SHALL provide `im.location` with `name`, `warehouse_id` (required, → `im.warehouse`), `type` (selection: internal, vendor, customer), and an optional zone-or-bin label.

#### Scenario: Create a location under a warehouse
- **WHEN** a Manager creates a location of type "internal" under an existing warehouse
- **THEN** the location is saved and listed under that warehouse

#### Scenario: Location requires a warehouse
- **WHEN** a Manager tries to save a location without selecting a warehouse
- **THEN** the system rejects the save with a validation error

### Requirement: Warehouses and locations are listed and viewable
The system SHALL provide list and form views for both models, reachable from menus under Inventory Management, with locations viewable from within their warehouse.

#### Scenario: Browse a warehouse's locations
- **WHEN** a user opens a warehouse's form
- **THEN** they see its locations listed (e.g. via a one2many or a linked list view)
