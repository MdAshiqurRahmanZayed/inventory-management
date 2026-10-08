# Spec Delta

## Purpose

Lets the system flag products that have fallen below their reorder level without a person having to check stock manually, by raising a trackable `im.alert` record and notifying the product's responsible user once a day.

## ADDED Requirements

### Requirement: Daily low-stock scan
The system SHALL run once per day and check every active `im.product` whose computed quantity on hand is below its `reorder_level`.

#### Scenario: Cron runs daily
- **WHEN** the scheduled low-stock check fires
- **THEN** every active product is evaluated against its reorder level

### Requirement: One open alert per under-stocked product
For each product found below its reorder level, the system SHALL ensure exactly one open `im.alert` record exists for that product, reusing an existing open alert instead of creating a duplicate.

#### Scenario: New alert created for newly low product
- **WHEN** a product drops below its reorder level and has no open alert
- **THEN** a new `im.alert` record is created for that product in an open state

#### Scenario: No duplicate alert for already-flagged product
- **WHEN** the daily scan runs and a product already has an open alert
- **THEN** no second alert is created for that product

#### Scenario: Alert does not reopen once resolved and stock still low
- **WHEN** a product's existing alert was manually closed and the product is still below reorder level on the next run
- **THEN** a new alert is created (closing is a resolution of that instance, not a permanent suppression)

### Requirement: Responsible user is notified by activity
When an alert is created, the system SHALL post a `mail.activity` on the product record assigned to the product's responsible user, or to a configured fallback user when the product has none.

#### Scenario: Activity posted to responsible user
- **WHEN** a new alert is raised for a product with a responsible user set
- **THEN** a mail activity for that product is created and assigned to that user

#### Scenario: Activity falls back when no responsible user
- **WHEN** a new alert is raised for a product with no responsible user set
- **THEN** a mail activity is created and assigned to the configured fallback user

### Requirement: Alert access follows role table
`im.alert` access SHALL match the README's table: Viewer read-only, User read/write (to close alerts) without create/delete, Manager full CRUD.

#### Scenario: User closes an alert
- **WHEN** a Stock User changes an open alert's state to closed
- **THEN** the write succeeds

#### Scenario: User cannot create or delete alerts
- **WHEN** a Stock User attempts to create or delete an `im.alert` record
- **THEN** the operation is denied

#### Scenario: Viewer cannot modify alerts
- **WHEN** a Stock Viewer attempts to write to an `im.alert` record
- **THEN** the write is denied
