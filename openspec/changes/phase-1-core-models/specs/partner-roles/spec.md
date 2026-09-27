## Purpose

Lets one Odoo contact act as a supplier, a customer, or both, so purchase and sales order forms (later phases) can filter to the right contacts without needing separate supplier/customer models.

## ADDED Requirements

### Requirement: Partner role field
`res.partner` SHALL have a `partner_role` selection field with values Supplier, Customer, and Both.

#### Scenario: Set a contact's role
- **WHEN** a Manager opens a contact's form and sets `partner_role` to "Both"
- **THEN** the value is saved and visible on the contact form

### Requirement: Computed supplier/customer flags
`res.partner` SHALL expose computed boolean fields `is_supplier` and `is_customer`, derived from `partner_role` (Supplier → is_supplier only; Customer → is_customer only; Both → both true).

#### Scenario: Both role computes both flags
- **WHEN** a contact's `partner_role` is "Both"
- **THEN** both `is_supplier` and `is_customer` read `True`

#### Scenario: Single role computes one flag
- **WHEN** a contact's `partner_role` is "Supplier"
- **THEN** `is_supplier` reads `True` and `is_customer` reads `False`

### Requirement: Role visible and filterable
The contact form and list view SHALL show `partner_role`, and it SHALL be usable as a search/filter field.

#### Scenario: Filter contacts by role
- **WHEN** a user filters the contacts list by "Supplier or Both"
- **THEN** only contacts with `is_supplier = True` appear
