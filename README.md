# Inventory Management

An Odoo inventory app (`inventory_management`) with its own OWL dashboard, plus a companion addon (`im_mcp`) that exposes a native **MCP server** — no separate process — so an AI assistant can check stock and draft stock moves through Odoo's own access rules.

## Status: Ongoing / Not Complete

This is an active, in-progress project. It is **not** production-ready. Core data models (products, categories, partner roles, warehouses, locations), purchasing, sales/adjustments, role-based access (Stock Viewer/User/Manager groups and record rules), low-stock alerts, a full OWL dashboard (stock value, low-stock, open orders, 7-day moves, top movers), a per-warehouse PDF stock report, and an MCP connector (global per-model access rules, generic record tools, a stock-move tool, and an audit log) are implemented.

## Naming note

This project was originally called "Stock Pilot". It has been renamed to **Inventory Management** to match this repository's name; the module technical name is `inventory_management` (previously `stock_pilot`).

## Odoo version note

This scaffold and its Docker environment run **Odoo 19**, per explicit project decision (the plan below was originally written against Odoo 18).

## Addons layout: `addons/` vs `extra-addons/`

- **`addons/`** — this project's own code (`inventory_management`). Committed to git.
- **`extra-addons/`** — third-party (OCA) modules. **Gitignored**, not committed — fetched on demand by `scripts/fetch-extra-addons.sh` (see below), so the repo doesn't vendor other people's source in git history.

### Included third-party module: OCA Web Responsive

[OCA's `web_responsive`](https://github.com/OCA/web/tree/19.0/web_responsive) (LGPL-3, © LasLabs, Tecnativa, ITerra, Onestein and other OCA contributors, unmodified, `19.0` branch) restores Odoo Enterprise's icon-grid app launcher/home menu in Community Edition. Fetched into `extra-addons/web_responsive/` by the script below. Installed independently — **not** a dependency of `inventory_management` — so `inventory_management` keeps depending only on `base` and `mail` as designed. Optional, but recommended for a nicer UI.

Fetch it (and any future OCA modules the script is extended to cover):
```bash
./scripts/fetch-extra-addons.sh
```
Safe to re-run — it skips any module already present in `extra-addons/`.

## Project Plan

### Goal

Build **Inventory Management**, a simple inventory app for Odoo with its own OWL dashboard, plus a built-in **MCP server** that lets an AI assistant check stock and draft stock moves through Odoo's own access rules. Plan for about 10 weeks of evenings and weekends. The data model follows the standard inventory ER designs from GeeksforGeeks and Kladana (see Sources).

- **Odoo module** (`inventory_management`): shows models, security, views, wizards, cron and **OWL frontend** work, which your resume does not show yet.
- **MCP connector**: shows API design, authentication and safe AI tool access, implemented as a native Odoo HTTP endpoint inside the same module — no separate server to deploy.
- Together they tell one story: a working business app that other systems and AI assistants can use safely.

### Scope

Keep it small and finished: one warehouse flow done well beats a half-built copy of Odoo Inventory. The module is standalone and depends only on `base` and `mail`, so reviewers can see every line is yours.

**In scope (v1)**

- Products with SKU, description, category, unit, cost, sale price, reorder level and a default supplier
- Product categories as their own model
- Suppliers and customers as Odoo contacts (`res.partner`) with a partner_role choice of Supplier, Customer or Both, so one contact can buy from you and sell to you
- Warehouses with an address and a capacity, each holding several locations (zones or bins)
- Purchase orders with order lines: confirming one creates the receipt moves
- Sales orders with order lines: confirming one creates a shipment with its own status and delivery moves
- Stock moves: receipt, delivery and internal transfer, going from Draft to Confirmed to Done
- Stock on hand per product and location, computed from Done moves
- Stock adjustments saved as records with type, quantity, reason and user, as an audit trail
- Low-stock alerts: a daily cron flags products below their reorder level and posts an activity to the responsible user
- Three roles: **Stock Viewer**, **Stock User** and **Stock Manager** (see Roles and access)
- OWL dashboard: stock value, low-stock list, open orders, moves in the last 7 days, top-moving products
- PDF stock report per warehouse

**Out of scope (v1)**

- Lots and serial numbers, barcodes, multi-company, accounting entries, invoices and payments, returns, pricing rules
- Note these as a v2 roadmap in the README; it shows you know where the product goes next.

### Architecture

The dashboard and the MCP server both go through Odoo's JSON-RPC API as a real user, so the same access rules protect people and AI alike. Keep them in two repos: `inventory_management` (the Odoo module) and `odoo-mcp` (the connector).

**Data model**

| Model | Key fields | Purpose |
| --- | --- | --- |
| `im.product` | name, sku, description, category, uom, cost, sale_price, reorder_level, supplier_id, qty_on_hand (computed) | What you stock |
| `res.partner` (Odoo core) | name, address, phone, email, contact person, partner_role (Supplier, Customer or Both), is_supplier and is_customer (computed from partner_role, used to filter order forms) | Suppliers and customers |
| `im.warehouse` | name, address, capacity, email | A physical site |
| `im.location` | name, warehouse_id, type (internal, vendor, customer), zone or bin | Where stock sits inside a warehouse |
| `im.purchase.order` | supplier_id, order_date, expected_date, state, amount_total | Buying from a supplier |
| `im.purchase.line` | order_id, product_id, quantity, unit_cost | One product on a purchase order |
| `im.sale.order` | customer_id, order_date, delivery_date, state, amount_total | Selling to a customer |
| `im.sale.line` | order_id, product_id, quantity, unit_price | One product on a sales order |
| `im.shipment` | sale_order_id, warehouse_id, shipment_date, status | A delivery leaving a warehouse |
| `im.move` | product_id, quantity, source_id, dest_id, state, done_date, user_id, purchase_line_id, shipment_id, adjustment_id | Every change in stock, from Draft to Confirmed to Done |
| `im.quant` | product_id, location_id, quantity | Current stock per location, updated when a move is Done |
| `im.adjustment` | product_id, location_id, type, quantity, reason, user_id, date | Stored audit trail of stock corrections |
| `im.alert` | product_id, level, state | Low-stock alerts raised by the daily cron |
| `im.api.log` | connector_id, user_id, tool, model, operation, inputs, result, allowed, create_date | Log of every MCP tool call |
| `im.mcp.connector, im.mcp.access` | see MCP connector | Which models and operations each MCP connector may use |

**ER diagram**

```mermaid
erDiagram
    RES_PARTNER ||--o{ IM_PRODUCT : supplies
    RES_PARTNER ||--o{ IM_PURCHASE_ORDER : "is supplier on"
    RES_PARTNER ||--o{ IM_SALE_ORDER : "is customer on"
    IM_PURCHASE_ORDER ||--|{ IM_PURCHASE_LINE : contains
    IM_PRODUCT ||--o{ IM_PURCHASE_LINE : "ordered in"
    IM_SALE_ORDER ||--|{ IM_SALE_LINE : contains
    IM_PRODUCT ||--o{ IM_SALE_LINE : "sold in"
    IM_SALE_ORDER ||--o{ IM_SHIPMENT : "shipped by"
    IM_WAREHOUSE ||--o{ IM_SHIPMENT : "ships from"
    IM_WAREHOUSE ||--|{ IM_LOCATION : contains
    IM_PRODUCT ||--o{ IM_QUANT : "stocked as"
    IM_LOCATION ||--o{ IM_QUANT : holds
    IM_PRODUCT ||--o{ IM_MOVE : "moved by"
    IM_LOCATION ||--o{ IM_MOVE : "source or destination"
    IM_PURCHASE_LINE ||--o{ IM_MOVE : "received by"
    IM_SHIPMENT ||--o{ IM_MOVE : "delivered by"
    IM_ADJUSTMENT ||--o| IM_MOVE : creates
    IM_PRODUCT ||--o{ IM_ADJUSTMENT : "corrected by"
    IM_PRODUCT ||--o{ IM_ALERT : raises

    IM_PRODUCT {
        int id PK
        string sku
        string name
        string category
        float cost
        float sale_price
        float reorder_level
        int supplier_id FK
    }
    RES_PARTNER {
        int id PK
        string name
        string email
        string partner_role
        bool is_supplier
        bool is_customer
    }
    IM_WAREHOUSE {
        int id PK
        string name
        string address
        float capacity
    }
    IM_LOCATION {
        int id PK
        int warehouse_id FK
        string type
    }
    IM_PURCHASE_ORDER {
        int id PK
        int supplier_id FK
        date order_date
        string state
    }
    IM_PURCHASE_LINE {
        int id PK
        int order_id FK
        int product_id FK
        float quantity
    }
    IM_SALE_ORDER {
        int id PK
        int customer_id FK
        date delivery_date
        string state
    }
    IM_SALE_LINE {
        int id PK
        int order_id FK
        int product_id FK
        float quantity
    }
    IM_SHIPMENT {
        int id PK
        int sale_order_id FK
        int warehouse_id FK
        string status
    }
    IM_MOVE {
        int id PK
        int product_id FK
        int source_id FK
        int dest_id FK
        int purchase_line_id FK
        int shipment_id FK
        int adjustment_id FK
        string state
    }
    IM_QUANT {
        int id PK
        int product_id FK
        int location_id FK
        float quantity
    }
    IM_ADJUSTMENT {
        int id PK
        int product_id FK
        int location_id FK
        string reason
    }
    IM_ALERT {
        int id PK
        int product_id FK
        string state
    }
```

Order lines are the bridge tables that turn the many-to-many between orders and products into two one-to-many links. Every receipt, delivery and adjustment ends as an `im.move`, and quants hold the resulting totals. `im.api.log` links only to `res.users` and is left out to keep the picture readable.

**Rules to enforce in code:** a Done move cannot be edited, stock cannot go below zero on an internal location, and every quantity change goes through `im.move`, so there is always an audit trail. Use full field names such as `product_id`, never shortcuts like `p_id`, and keep each fact in one place: prices and totals are computed from order lines, not stored twice. A purchase order only offers contacts whose role is Supplier or Both, and a sales order only Customer or Both, so the same company can appear on both sides.

### Roles and access

Three groups, each including the one below it, so a Manager automatically has everything a User has. Define them in `security/security.xml` under an **Inventory Management** category, with `implied_ids` linking Viewer to User to Manager.

| Group | Who it is for | Can do |
| --- | --- | --- |
| **Stock Viewer** | Sales staff, accountants, read-only AI keys | See products, stock, orders, shipments, moves and the dashboard |
| **Stock User** | Warehouse and purchasing staff | Everything a Viewer can, plus draft purchase and sales orders, create shipments, create and confirm moves, and close alerts |
| **Stock Manager** | Warehouse lead | Everything a User can, plus confirm purchase orders, run adjustments, manage products, suppliers, customers, warehouses and locations, and read the API log |

**Access per model** (`security/ir.model.access.csv`; R = read, W = write, C = create, D = delete)

| Model | Viewer | User | Manager |
| --- | --- | --- | --- |
| `im.product` | R | R | R W C D |
| `res.partner` (suppliers, customers) | R | R | R W C |
| `im.warehouse`, `im.location` | R | R | R W C D |
| `im.purchase.order`, `im.purchase.line` | R | R W C | R W C D |
| `im.sale.order`, `im.sale.line` | R | R W C | R W C D |
| `im.shipment` | R | R W C | R W C D |
| `im.move` | R | R W C | R W C D |
| `im.quant` | R | R | R |
| `im.adjustment` | none | R | R W C |
| `im.alert` | R | R W | R W C D |
| `im.api.log` | none | none | R |
| `im.mcp.connector, im.mcp.access` | none | none | R W C D |

**Record rules** (`security/rules.xml`)

- A User can edit only their own moves while they are Draft; Done moves are read-only for everyone.
- A User sees only the API log entries they created; a Manager sees all.
- Nobody writes `im.quant` directly: quantities change only when a move is set to Done, in code run with `sudo()` after the access check.
- Only a Manager can confirm a purchase order, so a User can prepare orders but not commit spending.

**How the MCP server fits:** each connector runs as a real user and also has its own access lines, so it gets the overlap of both. A connector for a Viewer can only read, even if its access lines tick write. Add a test for each role and each connector setting, for example that a User cannot open the adjustment wizard and that a connector without `can_create` on `im.move` is refused.

### MCP connector

The MCP server is not a separate process — it ships as its own Odoo app, `im_mcp` (depends on `inventory_management`, installed alongside it), exposing `POST /mcp/` (JSON-RPC 2.0, MCP streamable-HTTP transport) inside the same Odoo instance. Keeping it a separate module means the core inventory app stays free of MCP-specific models and tests, and the connector can be installed, upgraded, or removed independently. What MCP as a whole can touch is set once, globally, the same way Odoo's own access rights screen works — per-user scoping then comes entirely from each connector's bound user's existing Stock Viewer/User/Manager role.

**Setup in Odoo** (its own **MCP Connector** app, Manager only)

| Model | Key fields | Purpose |
| --- | --- | --- |
| `im.mcp.connector` | name, user_id, active, expires_on, rate_limit, last_used | One connection, for example "Claude Desktop, warehouse lead"; it always runs as its user. Authenticated by that user's own Odoo API key — no separate secret store |
| `im.mcp.access` | model_id, enabled, can_read, can_write, can_create, can_delete, field_ids, domain, max_records | One row per model (global — shared by every connector): whether MCP may use it at all, which operations, which fields, which records |
| `im.api.log` | connector_id, user_id, tool, model, operation, inputs, result, allowed, duration | Every call, allowed or refused |

**How each call is checked**

1. The caller presents an Odoo API key (`Authorization: Bearer <key>` or `X-API-Key`); Odoo resolves it to a user via `res.users.apikeys`, and the user must hold the **MCP User** group, or the call is refused.
2. Odoo finds that user's active, unexpired `im.mcp.connector`, or refuses the call.
3. The model's global `im.mcp.access` row must be enabled and allow the operation, for example `can_write`.
4. Odoo's own access rights and record rules for the connector's bound user must also allow it, so a connector can never do more than its user — the server never uses `sudo()` on the ORM call itself. Two connectors bound to users with different Odoo roles see different results from the same global rule.
5. Only the listed fields are read, the row's domain is added to every search, and results stop at `max_records`.
6. The call and its result are logged to `im.api.log`, allowed or refused.

**Tools** (JSON-RPC 2.0 envelope — the spec's reserved error codes `-32700`/`-32600`/`-32601`/`-32602`/`-32603`, plus our own `-32001` for an access/validation refusal; all built in `services/jsonrpc.py` so every response, success or error, is shaped the same way)

| Tool | What it does |
| --- | --- |
| `list_models` | Every model currently enabled for MCP, with its allowed operations — call this first, don't guess model names |
| `search_records` | Search a model: `domain`, `fields`, `limit`, `offset` |
| `get_record` | Read one record by ID, optionally restricted to `fields` |
| `create_record` | Create a record from `values` |
| `update_record` | Change `values` on a record |
| `delete_record` | Delete a record, only where `can_delete` is ticked |
| `draft_stock_move` | Validates product/source/destination, then creates an `im.move` in Draft |

Model names are this app's own (`im.product`, `im.warehouse`, `im.move`, …), **not** Odoo's standard `product.product`/`stock.*` models — those aren't part of this addon and will always be refused. `tools/list` now returns a real JSON Schema per tool (types, required fields) so a well-behaved client sends correct types; `limit`/`offset`/`record_id`/numeric args and `values`/`fields` are still coerced defensively (int-as-string, dict-as-JSON-string) in case a client sends them loosely anyway.

**Safety rules**

- Permission is the overlap of the model's global access rule and the connector's bound user's own Odoo rights.
- Deny by default: a model is unreachable through MCP until a Manager enables it. The refusal message names the exact model/operation and where to go fix it (MCP Connector app > Access Rules).
- Sensitive models (`res.users`, `im.api.log`, `ir.*`, `im.mcp.*`) can never be enabled for MCP.
- `field_ids` on an access rule is restricted to fields of that rule's own `model_id` — both in the UI (domain) and server-side (a constraint), since Odoo's Many2many domain alone is UI-only and wouldn't stop a field from a different model arriving via direct write/import.
- API keys are Odoo's own (Settings > Users > API Keys) — shown once, stored hashed, can expire and be revoked at any time.
- Each connector has a rate-limit field (not yet enforced) and every model's access rule has a result-row cap.

**Connecting an AI assistant**

1. In Odoo, add the user to the **MCP User** group (Settings > Users), then generate an API key for them (Settings > Users > that user > Account Security > API Keys > New). Copy it immediately — it's shown once.
2. As a Manager, open the **MCP Connector** app: create a connector for that user (Connectors), and under Access Rules, enable whichever models MCP as a whole should be able to reach (this applies globally, not just to this one connector).
3. Verify the server is reachable: `curl http://localhost:8069/mcp/health`.
4. **Claude Code** — add to the project's `.mcp.json` (keep it out of version control):
   ```json
   {
     "mcpServers": {
       "inventory": {
         "type": "http",
         "url": "http://localhost:8069/mcp/",
         "headers": { "Authorization": "Bearer <your-api-key>" }
       }
     }
   }
   ```
5. **Claude Desktop** doesn't speak HTTP transport directly — bridge with [`mcp-remote`](https://www.npmjs.com/package/mcp-remote) (needs Node.js) in `claude_desktop_config.json`:
   ```json
   {
     "mcpServers": {
       "inventory": {
         "command": "npx",
         "args": ["mcp-remote", "http://localhost:8069/mcp/", "--header", "Authorization:Bearer <your-api-key>"]
       }
     }
   }
   ```
   Restart Claude Desktop after saving.

This is a local/demo setup (static API key, no OAuth, no public hosting) — intentionally out of scope for Anthropic's connector directory, which requires OAuth 2.0 and an always-on public endpoint.

**Troubleshooting**

- **`mcp-remote` tries an OAuth browser flow instead of using your API key** — it caches OAuth client registrations per server URL in `~/.mcp-auth/mcp-remote-v1/`. If you (or another project) ever pointed `mcp-remote` at the same URL (e.g. another local Odoo also on `localhost:8069`) and it triggered OAuth once, that stale registration gets reused. Fix: quit the client, delete the matching `~/.mcp-auth/mcp-remote-v1/<hash>_*` files for that URL, reconnect.
- **"MCP is not allowed to '...' on '...'"** — expected, not a bug: that model has no `im.mcp.access` row, or the row doesn't grant that operation. The message says exactly where to enable it. Check you're using this app's own model names (`im.product`, not `product.product`).
- **A tool call 500s with a generic "Internal error"** — logged server-side with the real traceback (`_logger.exception` in `services/protocol.py`); the client never sees internals, by design. Check the Odoo log.

### Milestones

6 phases over 10 weeks, 5 gates. Do not start a phase until the gate before it passes. If time runs short, cut the PDF report and top movers before anything in the MCP phase, because the connector is what makes this project stand out.

### Testing and quality

Reviewers judge a repo in about two minutes, so tests and the README matter as much as features.

- **Odoo tests** (`TransactionCase`): purchase order to receipt, sales order to shipment and delivery, move flow and states, quant totals after each move, no negative stock, access for User versus Manager, the cron raising and closing alerts, the adjust wizard.
- **Dashboard test**: one OWL test (Hoot, Odoo's JS test framework) that the dashboard loads its figures.
- **MCP tests** (`pytest`): each tool with a mocked Odoo client, input validation, a connector without access to a model or operation getting a clear error, and sensitive models being refused.
- **Demo data**: about 20 products, 5 suppliers, 10 customers, 2 warehouses, a month of orders and moves, so the dashboard looks real on first install.
- **README**: what it does, a screenshot of the dashboard, a GIF of Claude drafting a stock move, install steps for both repos, and the v2 roadmap.
- **Code style**: follow Odoo's module layout and naming, and keep commits small with clear messages.

### Resume points (draft)

Use these once the project is built, and change any detail that ends up different.

> **Inventory Management** | GitHub | Demo
>
> - Built an **Odoo** inventory module covering **purchase and sales orders**, supplier receipts, customer shipments, per-location stock, audited **stock adjustments**, **low-stock alerts**, role-based **access rules**, and an **OWL dashboard**.
> - Built an **MCP server** that lets AI assistants check stock and orders and draft moves through Odoo's own permissions, with per-user **API keys**, model-based access that Managers set per connector in Odoo, and a full **audit log**.

### Sources

- [How to Design ER Diagrams for Inventory and Warehouse Management](https://www.geeksforgeeks.org/sql/how-to-design-er-diagrams-for-inventory-and-warehouse-management/), GeeksforGeeks: customer, product, supplier, warehouse, order and shipment entities.
- [ER Diagram for Inventory Management System](https://www.kladana.com/blog/inventory-management/er-diagram-for-inventory-management-system/), Kladana: purchase and sales orders, reorder level, stored stock adjustments, bridge tables and naming advice.

## Running with Docker

Requires Docker and Docker Compose.

1. Copy the example Odoo config file, and adjust if needed:
   ```bash
   cp odoo.conf.example odoo.conf
   ```
2. Fetch third-party addons (see "Addons layout" above):
   ```bash
   ./scripts/fetch-extra-addons.sh
   ```
3. Start Odoo + Postgres:
   ```bash
   docker compose up
   ```
   First run pulls the `odoo:19.0` and `postgres:16` images, which can take a few minutes.
4. Open Odoo in your browser at [http://localhost:8069](http://localhost:8069) and create/select a database. If port 8069 is already used by another project, edit the host-side port directly in `docker-compose.yml`'s `ports:` section (e.g. `"8169:8069"`).
5. Go to **Apps**, click **Update Apps List**, remove the "Apps" filter, search for **"Inventory Management"**, and click **Install**.
6. Confirm the module installs with no errors — `--with-demo` loads sample products, categories, warehouses, locations, and contacts, and the dashboard shows real counts on first load.
7. To enable the MCP connector, search for **"Inventory Management MCP Connector"** (`im_mcp`) and install it too — it shows as its own app (depends on `inventory_management`, adds nothing to the core app's models).
8. Optional: search for **"Web Responsive"** and install it too, for the icon-grid app launcher (click the waffle icon top-left after installing).

To stop the environment: `docker compose down` (add `-v` to also drop the database volume).

**Security note:** `odoo.conf` (copied from `odoo.conf.example`, gitignored) has placeholder `admin_passwd`/DB credentials. Change them if you ever run this somewhere reachable beyond your own machine.

## Running tests

Use `docker compose run --rm`, not `exec` — `run` spins up a one-off container without publishing port 8069, so it won't conflict with `docker compose up`'s already-running server (an `exec` into the running container tries to bind the same port a second time and fails with "Address already in use").

```bash
# Full test suite for both addons, against a disposable test db:
docker compose run --rm odoo odoo -d ci_test -i role_management,inventory_management,im_mcp \
  --test-enable --test-tags /inventory_management,/im_mcp \
  --stop-after-init --http-port=8169

# Just im_mcp:
docker compose run --rm odoo odoo -d ci_test -i role_management,inventory_management,im_mcp \
  --test-enable --test-tags /im_mcp \
  --stop-after-init --http-port=8169

# Re-run against an existing db without reinstalling:
docker compose run --rm odoo odoo -d ci_test \
  --test-tags /inventory_management,/im_mcp --stop-after-init --http-port=8169

# One test class/method only:
docker compose run --rm odoo odoo -d ci_test \
  --test-tags /inventory_management:TestPurchasing.test_receive_all_marks_moves_done \
  --stop-after-init --http-port=8169
```

`--http-port=8169` is belt-and-suspenders (picks a port nothing else binds); combined with `run` instead of `exec`, it's what lets this work alongside a live `docker compose up` session. No need to stop the dev server or kill local processes first.

## Repository layout

- `addons/inventory_management/` — this project's core Odoo module source (products, orders, stock, dashboard). Committed.
- `addons/im_mcp/` — the MCP connector, a separate installable addon depending on `inventory_management`. Committed.
- `extra-addons/` — third-party (OCA) modules, e.g. `web_responsive`. Gitignored; fetched via `scripts/fetch-extra-addons.sh`.
- `scripts/fetch-extra-addons.sh` — (re-)fetches everything under `extra-addons/`.
- `docker-compose.yml`, `odoo.conf.example` — local dev environment (copy `odoo.conf.example` to `odoo.conf`, gitignored; it's the single place DB credentials, admin password, and addons path are configured). Mounts both `addons/` and `extra-addons/` into the container at `/mnt/addons` and `/mnt/extra-addons` respectively.
- `openspec/` — [OpenSpec](https://openspec.dev) planning artifacts (proposals, specs, design, tasks) driving this project's development.
- `ruff.toml` — lint config for this repo's Python code (excludes vendored `extra-addons/`).
- `.github/workflows/ci.yml` — CI: ruff lint + both addons' tests run against Postgres via Docker Compose, on every push/PR to `main`.

## CI

On every push/PR to `main`:
- **Ruff lint** — `ruff check` against the repo (vendored `extra-addons/` excluded).
- **Odoo tests** — starts Postgres (waits for its healthcheck), then installs and runs both `inventory_management`'s and `im_mcp`'s test suites headlessly via `docker compose run`, isolated with `--test-tags /inventory_management,/im_mcp`.

Run the same checks locally:
```bash
ruff check
docker compose run --rm odoo odoo -d ci_test -i inventory_management --test-enable --test-tags /inventory_management --stop-after-init --http-port=8169
```

## Roadmap

Products, orders, moves, stock, role-based access, low-stock alerts, the full dashboard widget set, the per-warehouse PDF stock report, and the MCP connector are implemented — see `openspec/` for planning artifacts. Possible v2 items: lots/serial numbers, barcodes, multi-company, OAuth-based MCP auth for a public connector listing, rate-limit enforcement.
