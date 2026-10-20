# im_mcp — MCP Connector for Inventory Management

Native Odoo addon exposing `inventory_management` to AI assistants over the [Model Context Protocol](https://modelcontextprotocol.io). No separate server process — this runs inside Odoo's own HTTP stack.

Depends on `inventory_management`. Install it as a regular Odoo app (shows as its own tile, named "Inventory Management MCP Connector").

## How it works

One endpoint, `POST /mcp/`, speaking JSON-RPC 2.0 over MCP's streamable-HTTP transport (`Content-Type: application/json`). Every request is handled synchronously inside Odoo's request cycle — no background worker, no queue.

```
POST http://<host>/mcp/
Authorization: Bearer <your-odoo-api-key>
Content-Type: application/json

{"jsonrpc": "2.0", "id": 1, "method": "...", "params": {...}}
```

A health check needs no auth:

```bash
curl http://localhost:8069/mcp/health
# {"status": "ok", "server": "inventory-mcp", "version": "1.0.0"}
```

## Authentication

Every request (except `/mcp/health`) must carry an Odoo API key, either header works:

```
Authorization: Bearer <api-key>
X-API-Key: <api-key>
```

The key is a normal Odoo API key — generate one at **Settings > Users > (pick a user) > Account Security > API Keys > New**. It's shown once; copy it immediately.

Three gates, checked in order, any failure refuses the whole request:

1. **The key must resolve to an active user.** Validated through Odoo's own `res.users.apikeys._check_credentials()` — no custom secret storage.
2. **That user must hold the MCP User group.** Settings > Users > (user) > a new "MCP Access" row appears under their other access rights — tick "MCP User".
3. **That user must have an active, unexpired `im.mcp.connector` record.** Create one in the MCP Connector app (Connectors menu) — `user_id` set to that same user. This is a separate on/off switch from the group itself: a Manager can kill one integration (expire or deactivate its connector) without touching the user's actual Odoo login or API key.

A refusal at any of these three steps still gets logged to `im.api.log` (with `connector_id` empty if we never even got as far as resolving one), so misuse attempts are visible.

## Access control

What MCP as a whole is allowed to touch is controlled by `im.mcp.access` — **one row per model, global**, shared by every connector (not per-connector). Manager-only, under the MCP Connector app's **Access Rules** menu.

| Field | Meaning |
| --- | --- |
| `model_id` | Which Odoo model this rule governs (unique per model) |
| `enabled` | Master on/off switch for this model through MCP |
| `can_read` / `can_write` / `can_create` / `can_delete` | Which operations are allowed |
| `field_ids` | Optional — restrict reads to only these fields (must belong to `model_id`; enforced both in the UI picker and server-side) |
| `domain` | Optional extra domain ANDed into every search on this model |
| `max_records` | Cap on rows returned per `search_records` call (`0` = no records returned at all, not "unlimited" — explicit, not a default-falsy gotcha) |

A model with no row at all, or a disabled row, is completely unreachable — deny by default.

**This is not the only gate.** Every call also runs as the connector's real bound Odoo user, with their native Odoo access rights and record rules applied on top — the code never calls `sudo()` on the actual data operation. A Stock Viewer's connector and a Stock Manager's connector hitting the *same* enabled model can get very different results. Sensitive models (`res.users`, `im.api.log`, any `ir.*`, any `im.mcp.*`) can never be enabled, full stop.

## Tools

Call `tools/list` to get the live set with full JSON Schemas — the list below is current as of this writing. **Model names are this addon's own** (`im.product`, `im.warehouse`, `im.move`, …) — not Odoo's standard `product.product`/`stock.*` models, which aren't part of this app and will always be refused.

Arguments are tolerant of a client sending numbers as strings or objects/arrays as JSON-encoded strings (`"limit": "50"`, `"values": "{\"name\": \"x\"}"`) — coerced defensively rather than erroring, since not every MCP client respects the schema strictly.

### `list_models`

No arguments. Always call this first instead of guessing a model name.

```json
{"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {"name": "list_models", "arguments": {}}}
```

```json
{
  "jsonrpc": "2.0", "id": 1,
  "result": {"content": [{"type": "text", "text": "{\"models\": [{\"model\": \"im.product\", \"operations\": {\"read\": true, \"write\": false, \"create\": false, \"delete\": false}}]}"}]}
}
```

### `search_records`

| Arg | Type | Required | Notes |
| --- | --- | --- | --- |
| `model` | string | yes | |
| `domain` | array | no | Odoo domain, e.g. `[["name", "=", "Widget"]]` |
| `fields` | array of string | no | Restricts output further than the access rule's own `field_ids` (never widens it) |
| `limit` | integer | no | Default 10, capped by the model's `max_records` |
| `offset` | integer | no | Default 0 |

```json
{"jsonrpc": "2.0", "id": 2, "method": "tools/call", "params": {
  "name": "search_records",
  "arguments": {"model": "im.product", "domain": [["sku", "=", "ELE-0004"]], "fields": ["name", "sku", "cost"], "limit": 5}
}}
```

```json
{
  "jsonrpc": "2.0", "id": 2,
  "result": {"content": [{"type": "text", "text": "{\"records\": [{\"id\": 4, \"name\": \"27-inch Monitor\", \"sku\": \"ELE-0004\", \"cost\": 140.0}], \"count\": 1}"}]}
}
```

### `get_record`

| Arg | Type | Required |
| --- | --- | --- |
| `model` | string | yes |
| `record_id` | integer | yes |
| `fields` | array of string | no |

```json
{"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {
  "name": "get_record", "arguments": {"model": "im.product", "record_id": 4, "fields": ["name", "qty_on_hand"]}
}}
```

### `create_record`

| Arg | Type | Required |
| --- | --- | --- |
| `model` | string | yes |
| `values` | object | yes |

```json
{"jsonrpc": "2.0", "id": 4, "method": "tools/call", "params": {
  "name": "create_record",
  "arguments": {"model": "im.product.category", "values": {"name": "Seasonal"}}
}}
```

```json
{"jsonrpc": "2.0", "id": 4, "result": {"content": [{"type": "text", "text": "{\"id\": 12}"}]}}
```

### `update_record`

| Arg | Type | Required |
| --- | --- | --- |
| `model` | string | yes |
| `record_id` | integer | yes |
| `values` | object | yes |

### `delete_record`

| Arg | Type | Required |
| --- | --- | --- |
| `model` | string | yes |
| `record_id` | integer | yes |

Refused unless the model's access rule has `can_delete` ticked — off by default for every model.

### `draft_stock_move`

Specialized — not a generic `create_record` on `im.move`, because it validates the referenced records first and creates atomically (nothing is created on a validation failure).

| Arg | Type | Required | Notes |
| --- | --- | --- | --- |
| `product_id` | integer | yes | Must exist, and the connector must have read access to `im.product` |
| `quantity` | number | yes | Must be positive |
| `source_id` | integer | no | `im.location` id |
| `dest_id` | integer | no | `im.location` id — at least one of `source_id`/`dest_id` is required |

```json
{"jsonrpc": "2.0", "id": 5, "method": "tools/call", "params": {
  "name": "draft_stock_move",
  "arguments": {"product_id": 4, "quantity": 3, "dest_id": 1}
}}
```

```json
{"jsonrpc": "2.0", "id": 5, "result": {"content": [{"type": "text", "text": "{\"id\": 77, \"state\": \"draft\"}"}]}}
```

The move is created in **Draft** — confirming/receiving it is a separate step done in Odoo itself (or via `update_record` on `im.move` if that's been granted `can_write`).

## Request / response shape

Standard JSON-RPC 2.0 — see `services/jsonrpc.py` for the single place that builds every envelope.

**Request**
```json
{"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {"name": "...", "arguments": {...}}}
```
`id` omitted → treated as a notification, no response is sent.

**Success**
```json
{"jsonrpc": "2.0", "id": 1, "result": {"content": [{"type": "text", "text": "<JSON-encoded tool result>"}]}}
```
Tool results always come back as a JSON string inside a `text` content block — that's the MCP convention, not ours.

**Error**
```json
{"jsonrpc": "2.0", "id": 1, "error": {"code": -32001, "message": "MCP is not allowed to 'create' on 'im.product'. Ask a Manager to enable it: MCP Connector app > Access Rules > 'im.product' > tick 'create'."}}
```

| Code | Meaning |
| --- | --- |
| `-32700` | Parse error — the request body wasn't valid JSON |
| `-32601` | Unknown method |
| `-32603` | Internal error — an unexpected exception was caught and logged server-side; the client never sees the raw traceback |
| `-32001` | Our own "server error" band — access refusal, missing record, bad argument. The message is always actionable (names the model/operation and where to fix it) |

Every call, allowed or refused, is logged to `im.api.log` (tool, model, operation, inputs, allowed, duration) — see the MCP Connector app's **Call Log** menu.

## Other MCP methods

| Method | What it does |
| --- | --- |
| `initialize` | Handshake — returns `protocolVersion`, `serverInfo`, `capabilities` |
| `tools/list` | Returns every tool with its JSON Schema (`inputSchema`) |
| `tools/call` | Invokes one tool — see above |

No `resources/*` methods, no sessions, no SSE — each `/mcp/` request is handled statelessly; there's nothing in this tool set that needs multi-turn state.

## Connecting a client

See the main project README's **MCP connector > Connecting an AI assistant** section for `.mcp.json` (Claude Code) and `claude_desktop_config.json` (via `mcp-remote`) examples, plus a troubleshooting section for the common `mcp-remote` stale-OAuth-cache gotcha.

## Testing

```bash
docker compose run --rm odoo odoo -d ci_test -i inventory_management,im_mcp \
  --test-enable --test-tags /im_mcp --stop-after-init --http-port=8169
```
