# Proposal

## Why

The README is developer-centric (module layout, Docker setup, running tests, CI, contributing conventions). There is no document aimed at someone who just wants to *use* the app day-to-day — a warehouse user, a reviewer clicking through the UI, or a Manager setting up roles and the MCP connector for the first time — without reading code or openspec internals. A single root-level, task-oriented guide closes that gap.

## What Changes

- New `GUIDE.md` at the repo root: a short index/table of contents, one line per topic, linking out to individual pages under `docs/guide/` — not a single long page.
- New `docs/guide/` directory, one file per topic, each detailed enough to follow without the app open next to a short cheat sheet — expected results after each step, what the screen actually shows, and a short troubleshooting note where a step commonly trips people up:
  - `01-roles.md`, `02-dashboard.md`, `03-purchasing.md`, `04-sales.md`, `05-adjustments.md`, `06-alerts.md`, `07-stock-report.md`, `08-mcp-setup.md`, `09-mcp-connect.md`, `10-mcp-usage.md`
- README gets a one-line pointer at the top ("New to the app? See GUIDE.md") — no other README restructuring in this change.
- Not a replacement for `addons/im_mcp/README.md` (that stays the protocol/developer reference) — the MCP pages here are "how to turn it on and use it," not "how the JSON-RPC envelope works."

## Capabilities

(none — this is a documentation-only change; `skip_specs: true` is set in `.openspec.yaml`, no application behavior changes)

## Impact

- New file: `GUIDE.md` (repo root, short index).
- New directory: `docs/guide/` (10 topic pages).
- One-line edit to `README.md` (a pointer, not a rewrite).
- No code, schema, security, or test changes.
