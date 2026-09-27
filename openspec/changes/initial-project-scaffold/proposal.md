## Why

The repo currently has no code, only a project plan doc and OpenSpec tooling. Before any Inventory Management business logic can be built, the project needs an installable Odoo module skeleton, a way to run and verify it (Docker), and a README that orients a reviewer/collaborator and states the project is a work in progress.

## What Changes

- Add `README.md` at repo root: project summary, the full project plan embedded inline (goal, scope, data model, ER diagram, roles/access, MCP connector design, milestones — per instruction, not a link to an external file), an explicit **Status: Ongoing / Not Complete** notice, and setup/run instructions.
- Add minimal `inventory_management` Odoo module scaffold: `__manifest__.py`, `__init__.py`, empty `models/`, `security/ir.model.access.csv` stub, `views/` stub — depends only on `base` and `mail`, no business logic yet.
- Add `docker-compose.yml` + `odoo.conf.example` running Odoo 19 + Postgres, mounting `inventory_management` as a custom addon, so the module can be installed and verified via the Odoo Apps UI. All local config (DB creds, admin password, addons path) lives in `odoo.conf` alone — no `.env` file.
- Update README with Docker instructions: `docker compose up`, accessing Odoo, installing the module.
- Replace the app's placeholder landing action with a real page, and vendor OCA's `web_responsive` module (installed independently) to restore the icon-grid app launcher in Community Edition.

## Capabilities

### New Capabilities
- `module-scaffold`: A minimal, installable `inventory_management` Odoo module (manifest + empty structure) that Odoo recognizes and installs without errors, with no business logic.
- `docker-dev-environment`: A Docker Compose environment (Odoo 19 + Postgres) that mounts the module as a custom addon and lets a developer start Odoo and install/verify the module through the UI.

### Modified Capabilities
(none — no existing specs yet)

## Impact

- New files: `README.md`, `docker-compose.yml`, `odoo.conf.example`, `addons/inventory_management/**`, `scripts/fetch-extra-addons.sh`, `extra-addons/.gitkeep`.
- `extra-addons/web_responsive/**` (vendored OCA module, LGPL-3, unmodified) is fetched by the script, not committed — `extra-addons/` is gitignored.
- No existing code affected (repo currently empty besides OpenSpec tooling).
- No business logic, models, views, or security rules beyond the empty stub needed for Odoo to load the module.
