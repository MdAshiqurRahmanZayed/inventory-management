## Why

The scaffold (`initial-project-scaffold`) proved the module installs cleanly but has no data model at all. Every later phase (purchasing, sales, stock, dashboard, MCP) needs products, partners-with-a-role, warehouses and locations to exist first. This change lays that foundation.

## What Changes

- Add `im.product.category` (simple named category, no hierarchy needed for v1).
- Add `im.product`: SKU, description, category, unit of measure, cost, sale price, reorder level, default supplier — no `qty_on_hand` yet (that's computed from moves in a later phase; field is added here as a placeholder default 0.0 so later phases don't need a schema migration).
- Extend `res.partner` (no new model — reuse Odoo's own contacts) with a `partner_role` selection (Supplier / Customer / Both) and computed `is_supplier`/`is_customer` booleans, used later to filter order forms.
- Add `im.warehouse`: name, address, capacity, email.
- Add `im.location`: name, warehouse, type (internal/vendor/customer), zone or bin — belongs to a warehouse.
- Basic list/form views + menus for all four new models, plus a `res.partner` tweak (role field visible on the contact form).
- Real `ir.model.access.csv` rows for these models (Manager-only R/W/C/D for now — no role groups yet, that's Phase 4; using `base.group_system` as a placeholder single access level until Phase 4 introduces Viewer/User/Manager).
- Demo data: ~20 products, 5 suppliers, 10 customers, 2 warehouses (per plan doc's testing section), so the module looks real once installed.
- Basic Odoo tests (`TransactionCase`): each model creates/reads correctly, `partner_role` computed fields behave, no negative/invalid values slip through basic constraints.

## Capabilities

### New Capabilities
- `product-catalog`: Products and product categories can be created, viewed, and organized, with the fields needed by later purchasing/sales/stock phases.
- `partner-roles`: Contacts can be marked as Supplier, Customer, or Both, with computed flags later phases use to filter order forms.
- `warehouse-locations`: Warehouses and their internal locations (zones/bins) can be created and organized, forming the physical structure stock will later be tracked against.

### Modified Capabilities
(none — no existing specs yet; `initial-project-scaffold`'s specs describe the empty scaffold, not data model behavior)

## Impact

- New files under `addons/inventory_management/`: `models/im_product.py`, `models/im_product_category.py`, `models/im_warehouse.py`, `models/im_location.py`, `models/res_partner.py` (extension), matching `views/*.xml`, updated `security/ir.model.access.csv`, `demo/*.xml`, `tests/*.py`.
- `__manifest__.py` updated: add `data`/`demo` file lists; dependency list stays `base`, `mail` (no new dependency needed for these models).
- No change to the scaffold's landing page, Docker environment, or README plan section beyond noting progress.
