# Design

## Context

See proposal.md - Why. Current `security/` only has `ir.model.access.csv`, every row granting full CRUD to `base.group_system`; there is no `security.xml` or `rules.xml` yet. `im.move` has no "owner at Draft" field — `user_id` is named "Done By" and is only set in `_apply_done_stock_effect` when a move reaches Done (`models/im_move.py:46,123`), so "a User's own Draft move" must key off `create_uid`, not `user_id`. `im.quant._apply_move` already uses `self.sudo().with_context(im_allow_quant_write=True)` to bypass normal access when a move goes Done (`models/im_quant.py:32`) — the quant-protection record rule in this phase has to recognize that context flag as the only legitimate write path, not invent a new bypass. `im.purchase.order.action_confirm` currently has no permission check beyond normal `write` access (`models/im_purchase_order.py:95`). `im.product` has no responsible-user field today.

## Goals / Non-Goals

**Goals:**
- Replace every `base.group_system` line in `ir.model.access.csv` with the three real groups, matching the README's access table exactly.
- Add `security/rules.xml` with record rules for `im.move` (own-draft-write, done-read-only) and `im.quant` (no direct write).
- Gate `im.purchase.order.action_confirm` to Stock Manager without relying on a record rule (it's a state-transition method, not a CRUD check).
- Introduce `im.alert` + a daily cron that raises alerts and posts activities.
- Keep every existing Phase 1-3 test passing by having tests run as a role-appropriate user instead of implicit admin/system access.

**Non-Goals:**
- No UI permission-wizard, no per-field access (`field_ids`) — that's MCP connector territory in Phase 6.
- Not building `im.mcp.connector`/`im.mcp.access` in this phase; `access-control`'s "connector is bounded by its own user" requirement only needs to hold once those models exist later, so no code lands for it now beyond documenting the constraint in the spec.
- Not reworking `im.move.user_id`'s meaning ("Done By" stays as-is); ownership for record rules uses `create_uid` instead.

## Decisions

**Record-rule field for "own draft move" is `create_uid`, not `user_id`.**
`user_id` is only populated on Done, so it can't identify who drafted a move. `create_uid` is set by Odoo automatically on every record and is already indexed. Alternative considered: add a new `drafted_by` field defaulting to `env.uid` — rejected as redundant with `create_uid` and extra migration surface for no behavioral gain.

**PO confirm guard is an explicit group check in `action_confirm`, not a record rule.**
Record rules gate CRUD (read/write/create/unlink), not arbitrary method calls like a state-transition action. `action_confirm` already validates `order.state != "draft"` before proceeding (`models/im_purchase_order.py:97`); the same method adds `if not self.env.user.has_group("inventory_management.group_stock_manager"): raise AccessError(...)` at the top. Alternative considered: a `write` record rule keyed on `state == 'confirmed'` — rejected because Odoo record rules evaluate against the record's state *before* the write for `write` rules in some cases and are easy to get backwards for a single-field transition; an explicit check in the one method that performs the transition is simpler to reason about and test.

**Quant write-protection rule recognizes the existing `sudo()` + context-flag pattern, doesn't add a new one.**
`Quant._apply_move` already does `self.sudo().with_context(im_allow_quant_write=True)` (`models/im_quant.py:32`). The `im.quant` CRUD access rows in the CSV grant no group create/write/unlink at all (matches README: "R" only for every role), and `sudo()` bypasses `ir.model.access` entirely, so this requirement is already satisfied by the existing code once the CSV correctly has no write/create/unlink line for any group — no new record rule is needed for `im.quant` beyond keeping the access CSV at read-only for all three groups. The context flag is not and does not need to be enforced by a record rule; it's only used internally to avoid recursion concerns in `_apply_move`'s own sudo call.

**`im.alert`'s responsible-user lookup needs a `responsible_user_id` field added to `im.product`.**
The README's cron description ("posts an activity to the responsible user") presumes a per-product responsible user that doesn't exist on `im.product` today. Add `responsible_user_id = fields.Many2one("res.users")` (optional) to `im.product`. Alternative considered: use the product's `create_uid` — rejected because the person who created the product record is not necessarily who should be notified about its stock.

**Alert dedup key is `(product_id, state='open')`.**
A SQL/search constraint isn't used (Odoo doesn't support partial-unique constraints portably across its ORM); the cron does a `search` for an existing open alert per product before creating, inside the single cron transaction, so race conditions aren't a concern (cron runs single-threaded per scheduled job).

**Fallback user for alerts with no responsible user is a `res.config.settings`-backed system parameter**, not a hardcoded user. Falling back to `admin`/uid 1 silently is surprising in a fresh install with no admin activity; an unset fallback with no responsible user simply skips the activity (logged) rather than failing the cron for other products.

**Role Management menu reuses `res.users`, not a custom model.**
A Manager-only menu (`menuitem groups="inventory_management.group_stock_manager"`) opens a `res.users` list/form action scoped with `context={'default_groups_id': [...]}` or a simple form showing only the three inventory group checkboxes (via a dedicated `res.users` view inheriting the base form, filtered to the Viewer/User/Manager fields) — not a new `im.*` model. Odoo's `res.groups`/`res.users` relation already is the source of truth for group membership; building a parallel model would duplicate it and risk drifting out of sync. Alternative considered: a custom `im.role.assignment` wizard model — rejected as unnecessary complexity for what is fundamentally "edit this user's groups," and the existing `base.group_system`-era admin flow already proves `res.users` editing works for this.

**Existing tests move off implicit admin access.**
Phase 1-3 tests run as `self.env.ref("base.user_admin")` implicitly or don't set a user at all, inheriting superuser-like access in `TransactionCase`. Once `base.group_system` access is removed, these need a test user with the Stock Manager group (or the specific group the scenario needs) via `self.env["res.users"].create(...)` + `with_user()`, matching the standard Odoo testing pattern for access-controlled code.

## Implementation Notes (post-build corrections)

A few things the design above got wrong or missed, caught by actually running the test suite:

- **This Odoo build (19.0-20260926) restructured `res.groups`**: `category_id` was removed from `res.groups` in favor of `privilege_id` (→ a new `res.groups.privilege` record, which itself carries `category_id`). A privilege groups mutually-exclusive roles under one category — exactly Viewer/User/Manager — so `security.xml` creates one `res.groups.privilege` ("Role") under the Inventory Management category and points all three groups at it. `res.users.group_ids` (not `groups_id`) is the field name for group membership in this build; `ir.ui.menu.group_ids` (not `groups_id`) for menu visibility. `ir.cron` no longer has a `numbercall` field (crons just repeat indefinitely by default now).
- **TransactionCase runs as `base.user_root` (uid=1, OdooBot), not `base.user_admin`.** The Manager-only `has_group` check in `action_confirm` isn't bypassed by `env.su` for superuser — it's a real group-membership check — so `base.user_root` needed the Manager group too, not just `base.user_admin`. `security.xml` grants both, mirroring how core's own `group_system` seeds `user_ids`.
- **The `im.move` ownership rule was over-restrictive as scoped.** The original design keyed the User-write rule to `state == 'draft'` only, which — combined with Managers being implicitly also Stock Users via `implied_ids` — meant a Stock User couldn't progress their own move past Draft (confirm/receive), contradicting the README's "Everything a User can ... create and confirm moves." Fixed: the User-own-write rule now matches on `create_uid = user.id` alone, any non-Done state; the separate global Done-readonly rule still locks it down once Done. This doesn't weaken anything the spec's scenarios asserted — it only removes an accidental extra restriction the literal rule text implied.
- **`_apply_done_stock_effect`'s second `write()` call needed `sudo()`.** Completing a move writes `state: done` first, then immediately writes `done_date`/`user_id` in a follow-up `write()` call — but by then the record's state is already Done, so the new "Done is read-only for everyone" rule blocked that second write for every non-superuser, including the move's own owner completing their own move. Fixed by wrapping that bookkeeping write in `sudo()`, consistent with how `im.quant._apply_move` already treats post-transition system writes.

## Risks / Trade-offs

- [Removing `base.group_system` access could lock out demo data install or existing manual QA accounts] → Grant the three new groups to the module's demo users in demo data, and document in the PR description that any existing local dev user must be assigned a Stock role post-upgrade.
- [Record rules + explicit group checks add two different enforcement mechanisms (declarative XML vs. Python `has_group`) which future contributors could apply inconsistently] → Document the distinction in a short comment in `rules.xml` and in `action_confirm`: record rules for CRUD, explicit checks only for actions that aren't CRUD operations.
- [`responsible_user_id` is a new required-feeling field on an existing model with demo/production data already present] → Field is optional (`required=False`, no default), existing products simply have no responsible user and alerts fall back; no data migration needed.
- [Cron silently skipping the activity when no responsible user and no fallback configured could mean alerts go unnoticed] → The `im.alert` record itself is still created and visible to Viewer/User/Manager regardless of whether an activity could be posted, so the alert isn't lost — only the proactive notification is.

## Migration Plan

1. Land `security.xml` groups + `rules.xml` + rewritten `ir.model.access.csv` together in one upgrade (splitting them would leave the module with no access at all on models mid-migration).
2. Add demo data assigning the three groups to existing demo users so `--with-demo` installs remain usable.
3. Add `im.alert` model, views, menu, and cron in the same change (cron needs the access rows to exist to be referenced correctly).
4. Update existing Phase 1-3 tests to run `with_user()` as role-specific users; add new tests for groups, rules, and the cron.
5. Rollback: this is a fresh-feature module upgrade (not yet in any production install per README's "not production-ready" status), so rollback is reverting the commit/module version — no data migration to reverse since `im.alert` and `responsible_user_id` are additive.

## Open Questions

(none — field and enforcement choices above are settled; nothing here would change the specs or task breakdown if decided later)
