## 1. README

- [x] 1.1 Create `README.md` with project summary (Inventory Management module + odoo-mcp server, from plan doc)
- [x] 1.2 Add explicit **Status: Ongoing / Not Complete** section near the top
- [x] 1.3 Embed full plan doc content in README (not a link) per instruction
- [x] 1.4 Note Odoo version choice for this scaffold (19, vs plan doc's 18) and why
- [x] 1.5 Note module/project naming: repo and module are called **Inventory Management** (not "Stock Pilot" as in the original plan doc) and why

## 2. Odoo module scaffold (`addons/inventory_management`)

- [x] 2.1 Create `addons/inventory_management/__manifest__.py` (name, version `19.0.1.0.0`, category, summary, depends `["base", "mail"]`, data, license)
- [x] 2.2 Create `addons/inventory_management/__init__.py`
- [x] 2.3 Create empty `addons/inventory_management/models/__init__.py` (no models yet)
- [x] 2.4 Create `addons/inventory_management/security/ir.model.access.csv` with header row only
- [x] 2.5 Add a minimal top-level menu/action stub (e.g. empty landing view) so the installed app is visibly present in Odoo's app switcher
- [x] 2.6 Add `addons/inventory_management/static/description/icon.png` placeholder or omit if not required for install

## 3. Docker dev environment

- [x] 3.1 Create `docker-compose.yml` with `db` (Postgres) and `odoo` (odoo:19.0) services
- [x] 3.2 Mount `./addons` into Odoo's custom addons path
- [x] 3.3 Create `odoo.conf.example` (template): addons path, admin_passwd, and full DB connection (db_host/port/user/password) — the single place local config lives, no `.env`; `odoo.conf` gitignored and copied from the example
- [x] 3.4 ~~Create `.env.example`~~ — removed per instruction ("only odoo conf"); `docker-compose.yml` hardcodes matching Postgres creds and host port directly instead
- [x] 3.5 Create `.gitignore` (Docker volumes, `odoo.conf`, Python/Odoo/editor artifacts)

## 4. Documentation & verification

- [x] 4.1 Add README section: `docker compose up`, accessing Odoo at `localhost:<port>`, first-login/db creation steps
- [x] 4.2 Add README section: updating Apps list and installing "Inventory Management" module
- [x] 4.3 Verified: `docker compose up` starts cleanly (Odoo 19 + Postgres), `inventory_management` module installs headlessly (`odoo -i inventory_management --stop-after-init`) with 0 errors/tracebacks
- [x] 4.4 No install errors found. Found and fixed: default port 8069 can collide with other local Odoo projects (documented as a direct edit to `docker-compose.yml`'s `ports:` line); hardened `odoo.conf`'s placeholder `admin_passwd`; moved `odoo.conf` to `odoo.conf.example` + gitignore; consolidated all config into `odoo.conf` alone (removed `.env`/`.env.example`, hardcoded matching Postgres creds in `docker-compose.yml`) per instruction to use only `odoo.conf`; re-verified clean headless install after each config change
