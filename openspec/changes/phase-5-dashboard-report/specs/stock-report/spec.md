# Spec Delta

## Purpose

Lets a warehouse lead produce a printable, point-in-time record of what's on hand in one warehouse — for a physical count, a handover, or an external request — without building a query by hand.

## ADDED Requirements

### Requirement: Report is scoped to one warehouse
The stock report SHALL list only products with on-hand quantity in locations belonging to the selected warehouse.

#### Scenario: Other warehouses excluded
- **WHEN** a warehouse report is generated for Warehouse A
- **THEN** quantities held only in Warehouse B's locations do not appear on the report

### Requirement: Report lists product, SKU, quantity, and value
Each line of the report SHALL show the product's name, SKU, on-hand quantity in that warehouse, and the line's value (`quantity * cost`), with a grand total value at the end.

#### Scenario: Grand total sums the lines
- **WHEN** the report has lines valued at 100 and 250
- **THEN** the report's grand total shows 350

### Requirement: Zero-stock products are excluded
The report SHALL NOT list a product that has zero or no quant quantity in the selected warehouse.

#### Scenario: Product with no stock omitted
- **WHEN** a product has a quant record in the warehouse with quantity 0
- **THEN** that product does not appear as a line on the report

### Requirement: Report is triggered from the warehouse record
A warehouse's form or list view SHALL offer a way to generate this PDF report for that specific warehouse.

#### Scenario: Report opens scoped to the record it was triggered from
- **WHEN** a user generates the report from Warehouse A's form view
- **THEN** the resulting PDF is scoped to Warehouse A, not a prompt for which warehouse to choose
