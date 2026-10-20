# Design

## Context

See proposal.md - Why. Reference implementation studied: `serp_mcp` (a sibling Odoo project's native MCP addon) — proved the single-addon, no-separate-server pattern works: `POST /mcp/` controller → protocol dispatch → tool functions → ORM, auth via Odoo's own `res_users_apikeys` table. This design borrows that shape and narrows it to this project's scope (local use, no OAuth, no public directory listing — see prior conversation decisions).

## Goals / Non-Goals

**Goals:**
- No second repo/process — a second *addon* (`im_mcp`) inside the same Odoo instance, not a separate server
- Static Odoo API key auth only (reuse native hashing, no custom crypto)
- Global, per-model access rules (one row per model) on top of native Odoo permissions — matches `serp_mcp` exactly
- Minimal, readable code — no comment per line, no defensive code for cases that can't occur

**Non-Goals:**
- OAuth 2.0 / multi-tenant auth (would be needed for public directory listing — out of scope)
- Public/always-on hosting — local Docker + `.mcp.json` only
- MCP resources (`odoo://...` URIs), sessions, SSE streaming — not needed for the tool set here; stateless request/response is enough
- Rate limiting enforcement beyond storing the field (future work if this ever goes public)

## Decisions

**A second addon (`im_mcp`), not a separate `odoo-mcp` server.** Running inside Odoo's own WSGI stack means one deployable, one test suite, and direct ORM access — no second HTTP hop, no client library to keep in sync with the Odoo schema. `im_mcp` depends on `inventory_management` but ships as its own installable module (own `__manifest__.py`, own test suite) rather than being folded into `inventory_management` directly — keeps the core inventory app free of MCP-specific models/security/tests, and the connector can be installed, upgraded, or removed independently. Alternatives considered: (a) a standalone Python MCP server calling Odoo's JSON-RPC API externally (original plan) — rejected, pure overhead for a single-tenant local tool; (b) folding MCP code straight into `inventory_management` (first pass of this change) — reverted in favor of the separate-addon split once the user asked for it, since it's a cleaner boundary with no real cost (same repo, same `addons/` path, one `docker compose` stack).

**Auth via Odoo's native API key table, not a custom secret.** `im.mcp.connector` stores only metadata (name, user_id, active, expires_on, rate_limit, last_used) and points at a user; the actual secret lives in `res_users_apikeys`, created the normal Odoo way (Settings > API Keys). Validation reuses `KEY_CRYPT_CONTEXT.verify` the same way `serp_mcp` does. Alternative: custom hashed key column on `im.mcp.connector` — rejected, reinvents something Odoo already does safely.

**Global, one-row-per-model access rules — matches `serp_mcp`, not a per-connector extension.** An earlier pass of this design made `im.mcp.access` per-connector (`im.mcp.access(connector_id, model_id, ...)`), reasoning that different connectors might need to expose different model sets. Reverted after re-reading `serp_mcp`'s actual `mcp.access.rule` (`unique(model_id)`, no connector concept at all) and discussing the trade-off directly: per-connector access means every new connector starts from zero and needs its own grants re-entered per model, for a benefit (two connectors on the same Odoo role seeing different data) that isn't an actual requirement here. Global rules match the reference, are simpler to administer (enable a model once, every connector + user combination is scoped only by *that user's own native Odoo role*), and are still just as safe — `im.mcp.connector` is kept for identity, `active`/`expires_on` gating, rate-limit bookkeeping, and audit-log attribution, it just no longer carries its own access grants.

**Tools stay thin wrappers over the ORM.** `search_records`/`get_record`/`create_record`/`update_record`/`delete_record` check `im.mcp.access`, then call the ORM directly as the connector's user (no `sudo()`). `draft_stock_move` is the one specialized tool, because move creation has real validation (product/location existence) that generic `create_record` shouldn't have to special-case.

**No MCP session tracking.** `serp_mcp` creates `mcp.session` transient records per client for the `initialize` handshake. This project's tool set doesn't need multi-turn session state, so each `/mcp/` request is handled statelessly — one less model, one less thing to test.

## Risks / Trade-offs

- **Static API key, no scoping beyond `im.mcp.access`** → if a key leaks, the attacker gets everything that connector's user+access rows allow. Mitigated by `expires_on`, `active` toggle, and the audit log making misuse visible after the fact. Acceptable for a local/demo tool; would need OAuth before any public exposure.
- **No rate limiting enforced** → `rate_limit` field exists but isn't checked in this phase; a runaway client could hammer the endpoint. Low risk locally; flagged as follow-up if this ever goes public.
- **Stateless requests** → if a future tool genuinely needs multi-step state, this gets reworked. Not a concern for the current tool set.

## Migration Plan

Additive only — a new addon (`im_mcp`) plus one small, generic *Configuration* menu group added to `inventory_management` for it to parent under. No existing model's schema or access rights change. Install via `-i im_mcp` (after `inventory_management` is already installed/upgraded); rollback is simply uninstalling `im_mcp` or reverting the branch, since nothing here touches `inventory_management`'s own data.
