# Proposal

## Why

Every model in `security/ir.model.access.csv` currently grants full CRUD to `base.group_system` only, a placeholder used to get Phases 1-3 working without blocking on security design. No real Viewer/User/Manager distinction exists, so any non-admin user is locked out and there is no enforcement of the rules the README already promises (own-draft-move editing, Done-is-read-only, Manager-only PO confirm). Phase 4 replaces the placeholder with the real role model and adds the low-stock alerting the dashboard and README both reference but that doesn't exist yet (`im.alert` has no model, no cron).

## What Changes

- **BREAKING**: Remove all `base.group_system` access lines from `ir.model.access.csv` and replace with `im.group_stock_viewer` / `im.group_stock_user` / `im.group_stock_manager`, each model's R/W/C/D set per the README's Access-per-model table. Any non-admin user with no inventory group assigned loses access they previously got only by being an admin.
- Define three security groups in `security/security.xml` under a new "Inventory Management" category, with `implied_ids` chaining Viewer -> User -> Manager (Manager implies User implies Viewer).
- Add record rules (`security/rules.xml`):
  - `im.move`: a User can write only moves they created (`user_id`) while `state = 'draft'`; Done moves are read-only for every group (no write/unlink rule for anyone once Done).
  - `im.purchase.order`: only Manager can confirm (state -> `confirmed`); enforced in `action_confirm` via `check_access`/explicit group check, not just a record rule, since "confirm" is a state transition not a CRUD op.
  - `im.quant`: no group gets direct write/create/unlink via normal CRUD rules — quantities only change through code calling `sudo()` after a move is set to Done.
  - `im.alert`: User sees/writes (close) alerts; Manager has full CRUD; Viewer read-only.
- New `im.alert` model (`product_id`, `level`, `state`, link to the product's `reorder_level` comparison) plus list/form views and a menu entry under Inventory Management, access per the README table.
- New daily `ir.cron` that scans `im.product` for `qty_on_hand < reorder_level`, creates/reuses an open `im.alert` per product, and posts a `mail.activity` to the product's responsible user (falls back to a configurable default user if none set).
- Update demo data / existing tests that currently rely on implicit full access via `base.group_system` so they keep passing under the new groups (tests will assign a Viewer/User/Manager user explicitly instead of running as admin).

## Capabilities

### New Capabilities
- `access-control`: security groups (Viewer/User/Manager), `ir.model.access.csv` rewrite, and record rules governing draft/done moves, PO confirmation, and quant write-protection.
- `stock-alerts`: the `im.alert` model, its access/views, and the daily low-stock cron that raises alerts and creates activities.

### Modified Capabilities
(none — no capability specs have been archived yet for Phases 1-3; the access and cron behavior introduced here is new, not a change to a previously-specified capability)

## Impact

- `addons/inventory_management/security/ir.model.access.csv` — every row rewritten.
- `addons/inventory_management/security/security.xml` — new group category + 3 groups + `implied_ids`.
- `addons/inventory_management/security/rules.xml` — new file, record rules for `im.move`, `im.purchase.order` confirm guard, `im.quant`, `im.alert`.
- `addons/inventory_management/models/im_purchase_order.py` — `action_confirm` gains an explicit Manager-only check.
- `addons/inventory_management/models/` — new `im_alert.py`.
- `addons/inventory_management/views/` — new alert views + menu item.
- `addons/inventory_management/data/` — new `ir.cron` record for the daily low-stock scan.
- `addons/inventory_management/tests/` — existing tests updated to run as non-admin role users where they assert on access; new tests for groups, record rules, and the cron.
- `addons/inventory_management/__manifest__.py` — register `security/rules.xml` and the new alert views/data file.
