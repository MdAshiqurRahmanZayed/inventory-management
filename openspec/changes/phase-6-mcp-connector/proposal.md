# Proposal

## Why

The inventory app (products, orders, moves, stock, roles, alerts, dashboard) is implemented. The one thing that makes this project stand out as a portfolio piece — an AI assistant checking stock and drafting moves through Odoo's own permissions — is still missing. This phase adds that MCP connector.

## What Changes

- New Odoo model `im.mcp.connector`: one row per named connection (e.g. "Claude Desktop, warehouse lead"), wraps Odoo's own `res.users.apikeys` for the actual secret (no custom crypto).
- New model `im.mcp.access`: global, per-model grants (read/write/create/delete, field list, domain, max_records), one row per model, shared by every connector — matches `serp_mcp`'s `mcp.access.rule`. Sits on top of the calling connector's bound user's native Odoo permissions, never replacing them.
- New model `im.api.log`: one row per MCP call (connector, user, tool, model, operation, inputs, result, allowed, duration).
- New HTTP endpoint `POST /mcp/` inside a new addon, `im_mcp` (depends on `inventory_management`; no separate server process/repo), speaking MCP's JSON-RPC streamable-HTTP transport. Auth via Odoo API key (Bearer/X-API-Key header) + a gate group.
- Generic tools: `search_records`, `get_record`, `create_record`, `update_record`, `delete_record`, `list_models` — all checked against `im.mcp.access` before touching the ORM.
- One specialized tool: `draft_stock_move` — validates product/source/destination before creating an `im.move` in Draft, instead of leaving move creation to the generic `create_record` path.
- Backend UI: *Inventory Management > Configuration > MCP Connectors* (Manager only) — connector form with an access-lines sub-grid.
- Auth stays a static Odoo API key for this phase — no OAuth 2.0, no public hosting, no directory submission. Connect locally via `.mcp.json` (Claude Code) or `mcp-remote` (Claude Desktop).

## Capabilities

### New Capabilities

- `mcp-connector`: Odoo-native MCP server — connector/access-rule model, the `/mcp/` endpoint, generic CRUD tools plus `draft_stock_move`, and the audit log.

### Modified Capabilities

(none — this is additive; no existing requirement changes)

## Impact

- New addon `im_mcp` (depends on `inventory_management`): `models/im_mcp_connector.py`, `im_mcp_access.py`, `im_api_log.py`, `controllers/im_mcp_endpoint.py`, `services/` (protocol/tools), `security/`, `views/`.
- `inventory_management` itself only gains a generic, reusable *Configuration* menu group for `im_mcp`'s connector menu to parent under — no models, security rows, or MCP code of its own.
- No change to existing models' schemas or access rights — connectors ride on top of a real user's existing permissions.
- README: replace the "MCP connector lands in a later change" placeholder with setup/connect instructions, and document the two-addon layout.
