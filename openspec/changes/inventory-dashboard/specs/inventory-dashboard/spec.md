## Purpose

Gives a logged-in user a real landing page showing a snapshot of the current catalog and network (products, categories, warehouses, locations, suppliers, customers), replacing the static placeholder welcome message, without inventing stock/order data that doesn't exist yet.

## ADDED Requirements

### Requirement: Dashboard is the app's landing page
Opening the Inventory Management app SHALL show the dashboard, not a static message.

#### Scenario: Open the app
- **WHEN** a user clicks "Inventory Management" in the app switcher
- **THEN** the dashboard loads and displays current figures

### Requirement: Catalog and network counts
The dashboard SHALL display: total product count, total product category count, total warehouse count, total location count, total supplier count (contacts with role Supplier or Both), and total customer count (contacts with role Customer or Both).

#### Scenario: Counts match the database
- **WHEN** the dashboard loads
- **THEN** each displayed count equals the actual number of corresponding records

### Requirement: Products-per-category pie chart
The dashboard SHALL display a pie chart of product count per category.

#### Scenario: Chart reflects current products
- **WHEN** a category has 5 products
- **THEN** the pie chart's slice for that category corresponds to 5 products

### Requirement: Partner-role pie chart
The dashboard SHALL display a pie chart of contact count by role (Supplier, Customer, Both).

#### Scenario: Chart reflects current partner roles
- **WHEN** there are 5 Supplier-role, 10 Customer-role, and 1 Both-role contacts
- **THEN** the pie chart shows three slices sized 5, 10, and 1

### Requirement: No fabricated stock/order metrics
The dashboard SHALL NOT display stock value, low-stock alerts, open orders, or recent moves — those require data (stock moves, purchase/sales orders) that doesn't exist yet in this phase, and showing them from placeholder fields would be misleading.

#### Scenario: Dashboard omits unavailable metrics
- **WHEN** a user views the dashboard
- **THEN** no stock-value, low-stock, open-order, or recent-move widget is present
