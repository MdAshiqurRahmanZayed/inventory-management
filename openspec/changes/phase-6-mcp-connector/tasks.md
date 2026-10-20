# Tasks

> Note: tasks 1–6 below were implemented with the MCP code inside `inventory_management` itself. Task 7 records a later refactor — at the user's request — splitting all of it out into its own addon, `im_mcp` (depends on `inventory_management`). File paths in tasks 1–6 are historical (as of when each was written) and now live under `addons/im_mcp/` instead of `addons/inventory_management/`.

## 1. Connector and access models

- [x] 1.1 Add `models/im_mcp_connector.py`: `im.mcp.connector` (name, user_id, active, expires_on, rate_limit, last_used); add `ir.model.access.csv` row (Manager only); verify with a test: Manager can create/read, User cannot.
- [x] 1.2 Add `models/im_mcp_access.py`: `im.mcp.access` (connector_id, model_id, can_read/write/create/delete, field_ids, domain, max_records); constrain that `model_id` can never be `res.users`, `ir.*`, or `im.mcp.*`; verify with a test asserting the constraint raises on each of those model names.
- [x] 1.3 Add `models/im_api_log.py`: `im.api.log` (connector_id, user_id, tool, model, operation, inputs, result, allowed, duration, create_date); record rule so a User sees only their own rows, Manager sees all; verify with a test for both roles.
- [x] 1.4 Add `get_access(connector, model_name, operation)` on `im.mcp.access`: returns the matching row or `None`; verify with a test covering a granted model, an ungranted model, and an operation not enabled on a granted row.

## 2. Endpoint and auth

- [x] 2.1 Add `controllers/im_mcp_endpoint.py`: `POST /mcp/` route (`auth="none"`, manual auth inside), resolves the Odoo API key from `Authorization: Bearer` or `X-API-Key` into a user via Odoo's own `res.users.apikeys._check_credentials()`; verify with a test: valid key resolves the right user, invalid key is refused.
- [x] 2.2 Add MCP gate group `group_mcp_user` in `security/`; endpoint refuses any resolved user not in the group; verify with a test: valid key, user missing the group, call refused.
- [x] 2.3 Add JSON-RPC request/response plumbing (`services/protocol.py`): parse the incoming MCP method (`initialize`, `tools/list`, `tools/call`), dispatch to a tool function, return a JSON-RPC envelope; verify with a test round-tripping `initialize` and one `tools/call`.
- [x] 2.4 Add `GET /mcp/health` returning server name/version; verify by curling it and checking the JSON body.

## 3. Generic record tools

- [x] 3.1 Add `services/tools.py` `search_records`/`get_record`: check `im.mcp.access` (read), apply the access row's domain and `max_records` cap, read only `field_ids` when set; verify with tests for an allowed model, a model with no access row, and a domain/max_records that narrows results.
- [x] 3.2 Add `create_record`/`update_record`/`delete_record`: check the matching operation on `im.mcp.access`, then call the ORM as the connector's user (no `sudo()`); verify with tests for each operation allowed and each refused, plus one asserting a connector cannot exceed its own user's native Odoo permissions.
- [x] 3.3 Add `list_models`: returns only the models and operations the calling connector's own access rows grant; verify with a test comparing two connectors with different access rows.

## 4. Stock move tool and audit log

- [x] 4.1 Add `draft_stock_move` tool: validates product id, source location, destination location exist before creating an `im.move` in Draft; verify with tests for an invalid product (no record created) and a valid call (Draft move created with the given values).
- [x] 4.2 Wire every tool call (allowed or refused) to write one `im.api.log` row with connector, user, tool, model, operation, inputs, allowed, duration; verify with a test asserting a refused call still produces a log row with `allowed = false`.

## 5. Backend UI

- [x] 5.1 Add menu *Inventory Management > Configuration > MCP Connectors* (Manager only); connector form with an `im.mcp.access` sub-grid; verify with a test that the menu's `groups_id` includes Manager but not User, plus a manual open-as-each-role check in task 6.2.

## 6. Verification and documentation

- [x] 6.1 Rebuild/upgrade `inventory_management` in local Docker Odoo; fresh install with `--with-demo` loads with 0 errors. (The 11 `test_dashboard` failures are pre-existing on `main`, unrelated to this change — confirmed by running the same suite on `main` before implementing.)
- [x] 6.2 Manually generate an Odoo API key for a demo user, add them to `group_mcp_user`, create a connector + access rows, and exercise the live `/mcp/` endpoint end-to-end (health, initialize, `list_models`, `search_records`, `draft_stock_move`) against the running Docker instance; confirmed each call succeeds and is captured in `im.api.log`. (Caught and fixed a real bug: `json.dumps` on tool results failed on `datetime` fields — added `default=str`.) Connecting a real Claude Code/Desktop client to this same endpoint is the one remaining manual step for the user to do themselves with their own API key.
- [x] 6.3 Update README: replace the "MCP connector lands in a later change" placeholder with setup steps (generate API key, create connector, `.mcp.json` example) and flip the Status line.

## 7. Split into a separate addon

- [x] 7.1 Move all MCP code (`models/im_mcp_connector.py`, `im_mcp_access.py`, `im_api_log.py`, `controllers/`, `services/`, `views/im_mcp_connector_views.xml`, the three `tests/test_mcp_*.py` files) into a new addon `addons/im_mcp/`, depending on `inventory_management`; revert `inventory_management` back to only a generic, reusable *Configuration* menu group for `im_mcp` to parent under. Fix cross-module xmlid references (`im_mcp.group_mcp_user`, `inventory_management.group_stock_manager`, etc.) and have the moved tests import `BaseTransactionCase` from `odoo.addons.inventory_management.tests.common`; verify both modules install together with 0 errors and all 24 `im_mcp` tests plus the full `inventory_management` suite pass (same pre-existing 11 `test_dashboard` failures, 0 new).
- [x] 7.2 Code review (background agent against `serp_mcp`) found 5 real bugs: `group_mcp_user` sharing a privilege with the Viewer/User/Manager role ladder (broke the UI — gave it its own `res.groups.privilege`); `draft_stock_move` bypassing `im.mcp.access` for `im.product`/`im.location` via raw `.exists()` (fixed with an access-checked `_record_exists` helper); unhandled exceptions in `tools/call` leaking as non-JSON 500s (added a broad catch → `-32603`); auth refusals never logged (relaxed `im.api.log`'s required fields, log every refusal); `max_records = 0` silently uncapped (Odoo's own `search(limit=0)` returns *everything*, not nothing — special-cased `0`). Also blocked `im.api.log` itself as a sensitive model, added `field_ids` to the (then per-connector) access grid, added quantity validation. Verified with new/updated tests plus a live end-to-end pass against the running Docker instance.
- [x] 7.3 Made `im_mcp` a standalone app (`"application": True`) per request — gave it its own root menu + a distinct icon (not `inventory_management`'s), removed the now-unused *Configuration* menu stub from `inventory_management`. Added a proper **Call Log** screen (list/search view, matching `serp_mcp`'s activity-log pattern: allowed/refused decoration colors, filters, group-by) since there was previously no UI for `im.api.log` at all.
- [x] 7.4 Reverted `im.mcp.access` from per-connector to global, one-row-per-model (`unique(model_id)`) — see design.md's updated Decisions section for the full rationale. Dropped `connector_id` from `im.mcp.access` and `access_ids` from `im.mcp.connector`; dropped the now-unused `connector` parameter from every tool function in `services/tools.py` (`protocol.py` still passes `connector` through separately, for audit-log attribution only); added `enabled` per-model toggle (matches `serp_mcp`); replaced the per-connector access grid in the connector form with a new global **Access Rules** screen. Updated `list_models`/`get_access`/`get_enabled_models_info` to match `serp_mcp`'s own method names and shape. All tests and specs updated accordingly; reinstalled and reverified end-to-end.
