## Context

Repo is currently empty except OpenSpec tooling. See proposal.md for motivation. The original plan (kept alongside this repo, outside its tree) targeted Odoo 18, but this scaffold uses Odoo 19 per explicit instruction — module manifest and code should avoid anything that breaks on 19 (e.g. no reliance on deprecated APIs), and the README embeds the full plan content with the version choice noted.

## Goals / Non-Goals

**Goals:**
- A module Odoo can load and install with zero errors, with nothing to break as later changes add real models.
- A reproducible Docker environment any reviewer can start with one command.
- A README that is honest about project state (ongoing, not complete) and orients a reader in under two minutes.

**Non-Goals:**
- No product/order/move/stock models yet (later changes).
- No CI, no production deployment config.
- No `odoo-mcp` server code yet — out of scope for this change (mentioned in README only as a planned second component).

## Decisions

- **Odoo version: 19, not 18.** Plan doc says 18; user explicitly asked for Docker Odoo 19. Use the official `odoo:19.0` image. Manifest `version` field will read `19.0.1.0.0`.
- **Module location: `addons/inventory_management/`.** Keeps a clean top-level `addons/` custom-addons path to mount into Docker, separate from repo tooling (`openspec/`, `.claude/`).
- **Naming: "Inventory Management", not "Stock Pilot".** Plan doc uses "Stock Pilot"; project/repo/module are named Inventory Management instead per explicit instruction, matching the repo directory name. README notes this deviation from the plan doc. This also applies to the plan's example model prefix: `sp.*` (e.g. `sp.product`) is renamed to `im.*` (e.g. `im.product`) throughout the embedded plan in README, so a later change building real models doesn't reintroduce the discarded "Stock Pilot" name into technical identifiers.
- **Plan doc embedded in README, not linked.** Per explicit instruction, the full plan content (goal, scope, architecture, data model, ER diagram, roles/access, MCP connector, milestones, testing, resume points, sources) is copied into README.md directly rather than linking to the external plan doc file (which lives outside this repo and isn't a tracked project artifact).
- **Manifest depends: `base`, `mail` only** — per plan doc, keeps module self-contained and reviewable.
- **Stub views/security**: `ir.model.access.csv` ships with header row only (no models yet, so no access lines); `views/` stub is an empty menu placeholder file only if needed to prove the module loads a view — otherwise omit views entirely for v0 and add a minimal top-level menu item so installed module is visibly present in Odoo's app switcher (better manual verification than an entirely silent install).
- **Docker Compose, not Dockerfile-only.** Two services (`odoo`, `db`) — standard pattern for local Odoo dev, uses official images directly (no custom image build needed for scaffold stage).
- **Config via `odoo.conf` only, no `.env`.** All Odoo config (DB host/port/user/password, admin_passwd, addons_path) lives in one mounted file. `docker-compose.yml` hardcodes matching Postgres creds and the host port directly (edit the file to change either) instead of reading them from environment variables — per explicit instruction to keep exactly one place ("only odoo conf") a developer needs to look at/edit for local config. `odoo.conf.example` is the committed template; `odoo.conf` is gitignored. Odoo's docker entrypoint only injects its own env-derived DB args when a key is *absent* from `odoo.conf` (https://github.com/odoo/docker/blob/master/19.0/entrypoint.sh) — since we set `db_host`/`db_user`/`db_password` there, that file fully governs the DB connection and nothing silently overrides it.
- **Landing page: real `ir.actions.act_window` + `im.welcome` TransientModel, not `ir.actions.client` reload.** The reload-tag placeholder left the app menu just reloading the generic backend home with no real content. A minimal readonly-ish wizard form gives an actual "Inventory Management" page to land on, at negligible cost (no persisted data, no dependency change).
- **OCA `web_responsive` vendored, installed independently.** The Enterprise-style icon-grid app launcher (what the user wants to see on the waffle-menu click) is an Odoo Enterprise-only feature by default; Community only shows a compact text dropdown. `web_responsive` (OCA/web, `19.0` branch, LGPL-3, unmodified) restores it. Kept out of `inventory_management`'s `depends` so that module's own dependency list stays exactly `["base", "mail"]` per the existing spec requirement — `web_responsive` is a separate, optional dev-environment convenience, not part of the business module.
- **Two addons roots: `addons/` (ours, committed) vs `extra-addons/` (third-party, gitignored).** Per explicit instruction. Keeps the git history free of vendored third-party source; `scripts/fetch-extra-addons.sh` re-fetches it (sparse-clone from the upstream OCA repo, pinned to the `19.0` branch) on a fresh clone or whenever needed. `docker-compose.yml` mounts each root to its own container path (`/mnt/addons`, `/mnt/extra-addons`) and both are listed in `odoo.conf`'s `addons_path`, so the two stay clearly separated inside the container too, not just on disk.

## Risks / Trade-offs

- [Odoo 19 may differ from Odoo 18 plan assumptions in later changes] → Flag version choice prominently in README; revisit plan doc alignment before adding OWL dashboard (v18 vs v19 OWL API differences) in a later change.
- [Empty module could mask real install issues once models are added] → Cheap to catch early: this scaffold's only job is proving `docker compose up` + install works, giving a clean baseline to diff against later.
- [Docker image pull size/time on first run] → Documented in README as expected first-run cost; no mitigation needed for a dev-only setup.

## Open Questions

None — scope is fixed to scaffolding only; version and structure decisions above are final for this change.
