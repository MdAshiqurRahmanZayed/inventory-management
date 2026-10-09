# Spec Delta

## Purpose

Gives warehouse and purchasing staff an at-a-glance view of stock value, what's running low, what's still open, recent activity, and what's moving, without leaving the dashboard to check each model individually.

## ADDED Requirements

### Requirement: Dashboard shows total stock value
The dashboard SHALL display the total value of stock on hand, computed as the sum over all `im.quant` records of `quantity * product cost`.

#### Scenario: Stock value reflects quants and cost
- **WHEN** the dashboard loads
- **THEN** the displayed stock value equals the sum of `quantity * cost` across all quant records

#### Scenario: Empty stock shows zero
- **WHEN** no quant records exist
- **THEN** the displayed stock value is zero, not an error

### Requirement: Dashboard shows a low-stock count
The dashboard SHALL display the count of `im.alert` records currently in the `open` state.

#### Scenario: Low-stock count matches open alerts
- **WHEN** three products have open alerts and one has a closed alert
- **THEN** the dashboard's low-stock count is 3

### Requirement: Dashboard shows an open-orders count
The dashboard SHALL display the combined count of `im.purchase.order` and `im.sale.order` records whose state is `draft` or `confirmed`.

#### Scenario: Done and cancelled orders excluded
- **WHEN** there are 2 draft purchase orders, 1 confirmed sale order, 1 done purchase order, and 1 cancelled sale order
- **THEN** the dashboard's open-orders count is 3

### Requirement: Dashboard shows moves from the last 7 days
The dashboard SHALL display the count of `im.move` records whose `done_date` falls within the last 7 days, broken down by origin (receipt, delivery, adjustment).

#### Scenario: Moves outside the window excluded
- **WHEN** a move's `done_date` is 8 days ago
- **THEN** that move is not counted in the 7-day total

#### Scenario: Draft and confirmed moves excluded
- **WHEN** a move exists in Draft or Confirmed state with no `done_date`
- **THEN** that move is not counted in the 7-day total

### Requirement: Dashboard shows top-moving products
The dashboard SHALL display the 5 products with the highest total quantity moved across Done moves in the last 30 days, ranked descending.

#### Scenario: Ranking by moved quantity
- **WHEN** Product A has 50 units moved and Product B has 30 units moved in the last 30 days
- **THEN** Product A ranks above Product B in the top-movers list

#### Scenario: Fewer than 5 products with activity
- **WHEN** only 2 products have Done moves in the last 30 days
- **THEN** the top-movers list shows only those 2 products, not 5 placeholder entries

### Requirement: Widget data respects the viewer's model access
Each widget's underlying query SHALL run with the requesting user's normal access rights, so a widget never surfaces data that user could not otherwise read directly from its source model.

#### Scenario: Widget data never requires elevated access
- **WHEN** any Stock Viewer, User, or Manager opens the dashboard
- **THEN** every widget's figures are computed from models that role already has read access to
