# Spec Delta

## Purpose

Lets an AI assistant read stock/orders and draft stock moves against this Odoo instance through the same access rules that protect human users, via the Model Context Protocol.

## ADDED Requirements

### Requirement: Connector identity and API key
A connector SHALL be a named record (`im.mcp.connector`) bound to exactly one Odoo user, authenticated by that user's own Odoo API key (no separate secret store). A connector SHALL be usable only while `active` and before its `expires_on` date.

#### Scenario: Expired connector is refused
- **WHEN** an MCP request presents the API key of a connector whose `expires_on` has passed
- **THEN** the server refuses the call and does not execute any tool

#### Scenario: Inactive connector is refused
- **WHEN** an MCP request presents the API key of a connector with `active = false`
- **THEN** the server refuses the call and does not execute any tool

### Requirement: Global, per-model access rules
`im.mcp.access` SHALL have at most one row per model (enforced by a unique constraint), each declaring whether MCP as a whole may use it (`enabled`), which operations (read/write/create/delete) are allowed, an optional field allowlist, an optional domain, and a `max_records` cap. These rules apply uniformly to every connector and every user — there is no per-connector override. A model with no row, or a disabled row, SHALL be entirely unreachable through MCP.

#### Scenario: Model with no access row is refused
- **WHEN** any connector calls a tool against a model with no `im.mcp.access` row
- **THEN** the server refuses the call with an error naming the model

#### Scenario: Disabled rule is refused
- **WHEN** a model's `im.mcp.access` row has `enabled = false`
- **THEN** every connector's calls against that model are refused, regardless of the operation flags

#### Scenario: Operation not granted is refused
- **WHEN** a model's access row has `can_create = false`
- **THEN** a tool call that would create a record on that model is refused

#### Scenario: Domain restricts visible records
- **WHEN** a model's access row sets a domain
- **THEN** every search/read through MCP against that model is additionally filtered by that domain

#### Scenario: max_records caps results
- **WHEN** a model's access row sets `max_records` lower than a search's requested limit
- **THEN** the server returns at most `max_records` records

### Requirement: MCP access never exceeds the calling user's own permissions
The effective permission for any MCP call SHALL be the intersection of the global `im.mcp.access` rule for that model and the connector's bound user's native Odoo access rights and record rules. The tool path SHALL NOT use `sudo()` to bypass the user's own permissions — two connectors bound to users with different native Odoo roles SHALL see different results from the same global rule.

#### Scenario: Bound user lacks native permission
- **WHEN** a model's access row allows `write` but the calling connector's bound user's own Odoo access rights do not
- **THEN** the write is refused

### Requirement: Sensitive models are never reachable
`res.users`, `im.api.log`, any `ir.*` model, and `im.mcp.*` models SHALL NOT be assignable as the target of an `im.mcp.access` row.

#### Scenario: Attempt to grant access to a sensitive model
- **WHEN** a Manager tries to save an `im.mcp.access` row targeting `res.users`
- **THEN** the save is rejected with a validation error

### Requirement: Generic record tools
The server SHALL expose `search_records`, `get_record`, `create_record`, `update_record`, and `delete_record` tools that operate on any model enabled by the global `im.mcp.access` rules, and a `list_models` tool that lists every currently-enabled model and its allowed operations.

#### Scenario: list_models reflects the global rule set
- **WHEN** a model's `im.mcp.access` row is disabled or deleted
- **THEN** every subsequent `list_models` call, from any connector, stops listing that model

### Requirement: Stock move drafting tool
The server SHALL expose a `draft_stock_move` tool that validates product, source location, and destination location before creating an `im.move` in Draft state, atomically — no partially-created move on validation failure.

#### Scenario: Invalid product is rejected before create
- **WHEN** `draft_stock_move` is called with a product id that does not exist
- **THEN** the call fails with a clear error and no `im.move` record is created

#### Scenario: Valid call creates a Draft move
- **WHEN** `draft_stock_move` is called with a valid product, source, destination, and quantity
- **THEN** a new `im.move` record is created in Draft state with those values

### Requirement: Every call is audit-logged
Every MCP tool invocation, allowed or refused, SHALL produce one `im.api.log` row recording the connector, resolved user, tool name, target model, operation, inputs, whether it was allowed, and duration.

#### Scenario: Refused call is still logged
- **WHEN** a tool call is refused for any access reason
- **THEN** an `im.api.log` row is created with `allowed = false`

### Requirement: Endpoint authentication
The `/mcp/` endpoint SHALL require a valid Odoo API key (via `Authorization: Bearer` or `X-API-Key` header) belonging to a user in the MCP gate group. Requests without a valid key and group membership SHALL be refused before any tool executes.

#### Scenario: Valid key, user missing gate group
- **WHEN** a request presents a valid Odoo API key for a user not in the MCP gate group
- **THEN** the server refuses the call
