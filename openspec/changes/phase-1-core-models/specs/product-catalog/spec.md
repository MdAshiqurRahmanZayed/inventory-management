## Purpose

Lets a Manager define what the business stocks — products and their categories — with the fields purchasing, sales, and stock phases will build on top of.

## ADDED Requirements

### Requirement: Product categories
The system SHALL provide `im.product.category` with at least a required `name`, so products can be grouped.

#### Scenario: Create a category
- **WHEN** a Manager creates a category named "Electronics"
- **THEN** it is saved and selectable from the product form

### Requirement: Product record
The system SHALL provide `im.product` with: `name`, `sku` (required, unique), `description`, `category_id` (required, → `im.product.category`), `uom` (text for v1, no full UoM model), `cost`, `sale_price`, `reorder_level`, `supplier_id` (→ `res.partner`, domain restricted to Supplier/Both), and `qty_on_hand` (float, default 0.0, not yet computed from moves).

#### Scenario: Create a product
- **WHEN** a Manager creates a product with a unique SKU, a category, and a supplier
- **THEN** the product is saved and appears in the product list

#### Scenario: Duplicate SKU rejected
- **WHEN** a Manager creates a product whose SKU already exists on another product
- **THEN** the system rejects the save with a clear validation error

#### Scenario: Supplier field restricted to suppliers
- **WHEN** a Manager opens the supplier field on a product form
- **THEN** only contacts whose `partner_role` is Supplier or Both are selectable

### Requirement: Products are listed and viewable
The system SHALL provide list and form views for `im.product`, reachable from a menu under Inventory Management.

#### Scenario: Browse products
- **WHEN** a user opens the Products menu
- **THEN** they see a list of all products with SKU, name, category, and reorder level columns
