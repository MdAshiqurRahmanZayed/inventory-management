# Tasks

## 1. Security groups and access rewrite

- [x] 1.1 Add `security/security.xml` defining the "Inventory Management" category and three groups (`group_stock_viewer`, `group_stock_user`, `group_stock_manager`) with `implied_ids` chaining Manager -> User -> Viewer; verify by installing the module and confirming the groups appear under Settings > Users & Companies > Groups.
- [x] 1.2 Rewrite `security/ir.model.access.csv` replacing every `base.group_system` row with per-role rows matching the README's Access-per-model table exactly; verify with `ruff check` (no syntax regressions) and a manual install/upgrade with no access-related errors in the log.
- [x] 1.3 Register `security/security.xml` in `__manifest__.py`'s `data` list (before `ir.model.access.csv`, since groups must exist before the CSV references them); verify the module upgrades cleanly.
- [x] 1.4 Add demo data assigning Viewer/User/Manager groups to appropriate demo users so `--with-demo` installs remain usable; verify by installing with demo data and checking group membership in the UI.
- [x] 1.5 Add a "Role Management" menu item under Inventory Management (`groups="inventory_management.group_stock_manager"`) opening a `res.users` list/form scoped to the three inventory groups, with a dashboard-style tile icon matching the provided design; verify a Manager user sees and can use the menu, and a Viewer/User user does not see it in the menu tree.

## 2. Record rules and action guards

- [x] 2.1 Add `security/rules.xml` with the `im.move` own-draft-write rule (`create_uid = user.id` when `state = 'draft'`, Manager exempt) and register it in `__manifest__.py`; verify with a test: a User user can write their own Draft move, cannot write another user's Draft move.
- [x] 2.2 Add the Done-move read-only rule (no group has write/unlink once `state = 'done'`) to `rules.xml`; verify with a test: a Manager cannot edit a Done move.
- [x] 2.3 Add a Manager-only group check at the top of `im.purchase.order.action_confirm` (`models/im_purchase_order.py`), raising `AccessError` for non-Managers; verify with a test: a User calling `action_confirm` on a Draft PO is refused, a Manager succeeds.
- [x] 2.4 Confirm (by reading, not changing) that `im.quant`'s CSV rows grant no group write/create/unlink access, so the existing `sudo()` path in `_apply_move` remains the only write route; verify with a test: a Manager's direct `create`/`write` on `im.quant` is denied, while setting a move to Done still updates the quant total.

## 3. Low-stock alerts

- [x] 3.1 Add `responsible_user_id = fields.Many2one("res.users")` to `im.product` (`models/im_product.py`) and expose it on the product form view; verify the field saves and displays.
- [x] 3.2 Add `models/im_alert.py` with the `im.alert` model (`product_id`, `level`, `state` open/closed) and register it in `models/__init__.py`; verify the model installs and is visible in `ir.model`.
- [x] 3.3 Add `im.alert` rows to `ir.model.access.csv` per the README table (Viewer R, User R W, Manager R W C D); verify with access tests per role.
- [x] 3.4 Add list/form views for `im.alert` and a menu entry under Inventory Management, registered in `__manifest__.py`; verify by opening the menu in the UI.
- [x] 3.5 Add a system-parameter-backed fallback user setting for alert activities (used when a product has no `responsible_user_id`); verify the parameter is readable via `ir.config_parameter`.
- [x] 3.6 Implement the daily `ir.cron` (`data/ir_cron_low_stock.xml` or similar) calling a method that scans active products below `reorder_level`, creates/reuses one open `im.alert` per product, and posts a `mail.activity` to the responsible user or fallback; verify with a test: running the method twice for the same under-stocked product creates only one open alert.
- [x] 3.7 Verify the cron's activity-posting behavior with a test: a product with a responsible user gets an activity assigned to them; a product without one and a configured fallback gets an activity assigned to the fallback; a product without either gets an alert but no activity (and no error).

## 4. Update existing tests for real access control

- [x] 4.1 Audit Phase 1-3 tests (`tests/`) for implicit admin/system access now broken by the CSV rewrite; convert each affected test to create/use a role-specific test user and `with_user()`; verify the full suite passes: `docker compose run --rm odoo odoo -d ci_test -i inventory_management --test-enable --test-tags /inventory_management --stop-after-init --http-port=8169`.
- [x] 4.2 Add a dedicated access-control test module (`tests/test_access_control.py`) covering the `access-control` spec's scenarios not already covered in 2.x, plus `tests/test_access_matrix.py` asserting the full Viewer/User/Manager x R/W/C/D matrix against every model in the README's Access-per-model table; verify it passes in the same test run as 4.1.

## 5. Documentation

- [x] 5.1 Update README's "Status" line and Milestones section to mark Phase 4 complete (roles, access, alerts) once the above lands; verify by reading the rendered section for accuracy against what was actually built.
