# Spec Delta

## Purpose

Defines the three Inventory Management security groups and the per-model, per-record access rules that let Viewer/User/Manager roles (and, by extension, MCP connectors running as a given user) interact with the module's data only to the extent the README's Roles and Access tables allow.

## ADDED Requirements

### Requirement: Three chained security groups
The system SHALL define three groups — Stock Viewer, Stock User, Stock Manager — under an "Inventory Management" category, where Stock Manager implies Stock User and Stock User implies Stock Viewer, so a user in a higher group automatically holds every lower group's access.

#### Scenario: Manager has Viewer and User access
- **WHEN** a user is added only to the Stock Manager group
- **THEN** that user's effective groups include Stock User and Stock Viewer

#### Scenario: Viewer does not gain User or Manager access
- **WHEN** a user is added only to the Stock Viewer group
- **THEN** that user does not gain Stock User or Stock Manager permissions

### Requirement: Per-model access matches the role table
Each model's `ir.model.access.csv` entries SHALL grant exactly the read/write/create/delete combination defined in the README's Access-per-model table for Viewer, User, and Manager, and SHALL NOT grant any access to `base.group_system` as a stand-in for a role.

#### Scenario: Viewer is read-only on products
- **WHEN** a Stock Viewer user opens `im.product`
- **THEN** the user can read records but cannot write, create, or delete them

#### Scenario: User can draft but not confirm purchase orders
- **WHEN** a Stock User user creates an `im.purchase.order`
- **THEN** the create and write succeed
- **AND** the user has no delete access on `im.purchase.order`

#### Scenario: Manager has full CRUD on warehouses
- **WHEN** a Stock Manager user creates, edits, or deletes an `im.warehouse`
- **THEN** all four operations succeed

#### Scenario: Viewer has no access to adjustments
- **WHEN** a Stock Viewer user attempts to read `im.adjustment`
- **THEN** access is denied

#### Scenario: No role grants direct access to API logs except Manager
- **WHEN** a Stock Viewer or Stock User user attempts to read `im.api.log`
- **THEN** access is denied
- **WHEN** a Stock Manager user reads `im.api.log`
- **THEN** the read succeeds and no write/create/delete is granted

### Requirement: Users edit only their own moves
A Stock User SHALL be able to write to an `im.move` record only when they created it (so they can draft, confirm, and receive their own moves end to end); a Stock Manager is not restricted by move ownership. This is independent of the separate Done-is-read-only requirement below, which still locks the record once it reaches Done regardless of ownership.

#### Scenario: User edits their own draft move
- **WHEN** a Stock User who created a Draft move edits its quantity
- **THEN** the write succeeds

#### Scenario: User cannot edit another user's move
- **WHEN** a Stock User attempts to edit a move created by a different user
- **THEN** the write is denied

#### Scenario: User confirms and receives their own move
- **WHEN** a Stock User who created a move transitions it from Draft to Confirmed and then to Done
- **THEN** both writes succeed

#### Scenario: Manager edits any non-Done move
- **WHEN** a Stock Manager edits a move created by another user
- **THEN** the write succeeds

### Requirement: Done moves are read-only for everyone
Once an `im.move` record's `state` is `done`, no group — including Stock Manager — SHALL be able to write to or delete that record through normal access.

#### Scenario: Manager cannot edit a Done move
- **WHEN** a Stock Manager attempts to edit a move whose state is Done
- **THEN** the write is denied

#### Scenario: Done move remains readable
- **WHEN** any Stock Viewer, User, or Manager reads a Done move
- **THEN** the read succeeds

### Requirement: Only a Manager can confirm a purchase order
Confirming an `im.purchase.order` (transitioning it out of Draft) SHALL be restricted to users in the Stock Manager group, independent of the model's normal write access.

#### Scenario: User cannot confirm a purchase order
- **WHEN** a Stock User who has write access to a Draft purchase order attempts to confirm it
- **THEN** the confirm action is refused

#### Scenario: Manager confirms a purchase order
- **WHEN** a Stock Manager confirms a Draft purchase order
- **THEN** the order transitions to Confirmed and its receipt moves are created

### Requirement: Quants are never written directly by a role
No group SHALL have create, write, or delete access to `im.quant` through normal CRUD; quantities change only as a side effect of a move being set to Done, executed with elevated privileges after the move's own access check has passed.

#### Scenario: Manager cannot create a quant directly
- **WHEN** a Stock Manager attempts to create an `im.quant` record through the UI or a direct write
- **THEN** the create is denied

#### Scenario: Quant updates when a move completes
- **WHEN** a Stock User with access to complete their own Draft move sets it to Done
- **THEN** the corresponding `im.quant` quantity is updated as a system-level side effect, not a direct user write

### Requirement: Connector access is bounded by its running user
An MCP connector's effective permissions on any model SHALL never exceed the intersection of its own `im.mcp.access` lines and the access rules of the Odoo user it runs as.

#### Scenario: Connector cannot write beyond its user's role
- **WHEN** a connector's access line allows write on `im.move` but the connector's user is only a Stock Viewer
- **THEN** write attempts through the connector are denied

### Requirement: Role Management menu is Manager-only
The system SHALL provide a "Role Management" menu entry under Inventory Management that lets a user assign the Viewer/User/Manager groups to other users, and this menu SHALL be visible only to members of the Stock Manager group.

#### Scenario: Manager sees and uses Role Management
- **WHEN** a Stock Manager opens the Inventory Management app
- **THEN** the Role Management menu is visible
- **AND** opening it lets the Manager add or remove a user's Viewer/User/Manager group membership

#### Scenario: Viewer and User do not see Role Management
- **WHEN** a Stock Viewer or Stock User opens the Inventory Management app
- **THEN** the Role Management menu is not visible to them

#### Scenario: Role Management cannot grant access beyond the three inventory groups
- **WHEN** a Manager uses Role Management to change a user's role
- **THEN** only Stock Viewer/User/Manager membership is affected
- **AND** no other unrelated Odoo group or permission is exposed for editing through this menu
