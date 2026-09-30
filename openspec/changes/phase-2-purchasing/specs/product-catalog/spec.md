## MODIFIED Requirements

### Requirement: Product record
The system SHALL provide `im.product` with: `name`, `sku` (required, unique), `description`, `category_id` (required, → `im.product.category`), `uom` (text for v1, no full UoM model), `cost`, `sale_price`, `reorder_level`, `supplier_id` (→ `res.partner`, domain restricted to Supplier/Both), and `qty_on_hand` (computed, read-only, the sum of that product's `im.quant` rows across all locations).

#### Scenario: Create a product
- **WHEN** a Manager creates a product with a unique SKU, a category, and a supplier
- **THEN** the product is saved and appears in the product list

#### Scenario: Duplicate SKU rejected
- **WHEN** a Manager creates a product whose SKU already exists on another product
- **THEN** the system rejects the save with a clear validation error

#### Scenario: Supplier field restricted to suppliers
- **WHEN** a Manager opens the supplier field on a product form
- **THEN** only contacts whose `partner_role` is Supplier or Both are selectable

#### Scenario: qty_on_hand reflects stock across locations
- **WHEN** a product has quant rows of 10 at one location and 5 at another
- **THEN** its `qty_on_hand` shows 15

#### Scenario: qty_on_hand is zero with no stock
- **WHEN** a product has never had a `im.quant` row
- **THEN** its `qty_on_hand` shows 0
