## 1. Product catalog

- [x] 1.1 Create `models/im_product_category.py` (`im.product.category`: `name`)
- [x] 1.2 Create `models/im_product.py` (`im.product`: `name`, `sku` unique, `description`, `category_id`, `uom`, `cost`, `sale_price`, `reorder_level`, `supplier_id` domain-restricted to Supplier/Both, `qty_on_hand` placeholder float default 0.0)
- [x] 1.3 Add SQL/Python unique constraint on `sku` (via `models.Constraint`, the Odoo 19 API — `_sql_constraints` is deprecated)
- [x] 1.4 Create list/form views + menu for `im.product.category`
- [x] 1.5 Create list/form views + menu for `im.product`

## 2. Partner roles

- [x] 2.1 Create `models/res_partner.py` (`_inherit = "res.partner"`): `partner_role` selection (Supplier/Customer/Both), stored computed `is_supplier`/`is_customer`. Field labeled "Business Role" (not "Role") to avoid a label collision with `res.users`' own `role` field.
- [x] 2.2 Extend the contact form view to show `partner_role`
- [x] 2.3 Make `partner_role`/`is_supplier`/`is_customer` searchable/filterable in the contacts list view

## 3. Warehouses & locations

- [x] 3.1 Create `models/im_warehouse.py` (`im.warehouse`: `name`, `address`, `capacity`, `email`)
- [x] 3.2 Create `models/im_location.py` (`im.location`: `name`, `warehouse_id` required, `type` selection internal/vendor/customer, zone/bin label)
- [x] 3.3 Create list/form views + menu for `im.warehouse`, with locations visible from the warehouse form (one2many editable list)
- [x] 3.4 Create list/form views + menu for `im.location`

## 4. Security & manifest

- [x] 4.1 Add `ir.model.access.csv` rows for all 4 new models (`base.group_system`, full R/W/C/D) — explicitly temporary, replaced in Phase 4
- [x] 4.2 Update `__manifest__.py`: add new `data` (views, security) and `demo` (demo data) file lists

## 5. Demo data

- [x] 5.1 Create `demo/im_demo_data.xml`: 5 supplier contacts (partner_role=Supplier, one also Both), 10 customer contacts (partner_role=Customer), 2 warehouses with 2 locations each, 20 products across 3 categories (Electronics, Office Supplies, Furniture)

## 6. Tests

- [x] 6.1 `TransactionCase` test: create category → create product referencing it → fields persist correctly
- [x] 6.2 `TransactionCase` test: duplicate SKU on a second product raises a validation error
- [x] 6.3 `TransactionCase` test: partner_role="Both" computes both is_supplier/is_customer True; single role computes only its own flag
- [x] 6.4 `TransactionCase` test: warehouse + location creation, location without warehouse_id rejected
- [x] 6.5 (added) `TransactionCase` tests for remaining required-field constraints: category requires name, product requires category, product requires SKU, warehouse requires name, location defaults to type "internal"
- [x] 6.6 (added) `TransactionCase` test: `res.partner.search([('is_supplier', '=', True)])` returns suppliers and excludes customers

## 7. Verification

- [x] 7.1 Rebuilt/upgraded `inventory_management` in the local Docker Odoo; fresh install with `--with-demo` loads all demo data (20 products, 3 categories, 2 warehouses, 4 locations, 5 suppliers, 10 real customers + 1 dual-role) with 0 errors
- [x] 7.2 Manually browsed in the running Docker Odoo: Products list (20 rows, correct columns), Warehouses list, Locations list (correctly linked to warehouses), and a Contact form showing "Business Role: Supplier" — all views render correctly
- [x] 7.3 Ran tests headlessly isolated to this module (`odoo -d <db> -i inventory_management --test-enable --test-tags /inventory_management --stop-after-init`): 0 failed, 0 errors, all 12 test methods pass. (Also ran the full unfiltered `--test-enable` suite once: 3 failed/20 errors across ~1888 tests, all in unrelated pre-existing core Odoo modules — base/mail/etc — not `inventory_management`, confirmed via the isolated re-run.)

### Notes on issues found and fixed during verification
- `_sql_constraints` is deprecated in Odoo 19 (warning at load); replaced with `models.Constraint` per the new ORM API.
- `partner_role`'s default label "Role" collided with `res.users`' own "Role" field label; renamed to "Business Role".
- `res_partner_views.xml`'s list-view xpath anchored on a `name` field that doesn't exist in Odoo 19's `base.view_partner_tree` (it uses `display_name` instead) — fixed the anchor, verified against the actual base view XML before retrying.
- A stray `docker compose run --service-ports` container from an earlier manual session held port 8069 and cached a stale database list, causing "Database not found" for newly created test databases — identified via `docker ps`, removed, and the proper `docker compose up -d odoo` service restarted.
