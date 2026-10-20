# Tasks

> Note: an earlier pass of this change wrote everything into one `GUIDE.md` page. Reworked, at the user's request, into `GUIDE.md` as a short index + separate pages under `docs/guide/`, each with more depth (expected results per step, what the screen shows, a troubleshooting note where relevant) — not just split, expanded.

## 1. Scaffold

- [x] 1.1 Create `docs/guide/` directory.
- [x] 1.2 Rewrite `GUIDE.md` at the repo root as a short index: who it's for, how it differs from README, one line + link per page below; verify by clicking every link and confirming each resolves to a real file.

## 2. Roles and dashboard

- [x] 2.1 Write `docs/guide/01-roles.md`: all five roles (Stock Viewer/User/Manager, MCP User/Admin) in depth — what each can see/do, how to tell which role you have, how a Manager assigns one; verify against `security/security.xml`'s `implied_ids` and `im_mcp/security/security.xml`'s privilege setup.
- [x] 2.2 Write `docs/guide/02-dashboard.md`: every tile and chart explained (what it counts, how it's computed in plain language, what an empty/zero state looks like), the Top Movers list, how the 7-day/30-day windows work; verify against `models/im_dashboard.py` and a fresh `--with-demo` install.

## 3. Purchasing, sales, adjustments, alerts, reporting

- [x] 3.1 Write `docs/guide/03-purchasing.md`: full purchase-order lifecycle (Draft → Confirm → Receive All → Mark Done, or Cancel), who can do each step, what happens to stock at each transition, a troubleshooting note for "why can't I confirm this order" (Manager-only step); verify against `im_purchase_order_views.xml` and `action_confirm`/`action_receive_all`/`action_done`/`action_cancel`.
- [x] 3.2 Write `docs/guide/04-sales.md`: full sale-order lifecycle (Draft → Confirm → Deliver All → Mark Done, or Cancel), the shipment created on confirm, what happens when you try to over-deliver; verify against `im_sale_order_views.xml` and `action_deliver_all`.
- [x] 3.3 Write `docs/guide/05-adjustments.md`: when to use one vs. a regular move, increase vs. decrease, why `reason` is mandatory, who can create one; verify against `models/im_adjustment.py`'s required field and the Manager-only access row.
- [x] 3.4 Write `docs/guide/06-alerts.md`: the daily cron, reorder level, where the alert shows (dashboard count + the product's own activity), closing an alert, what re-triggers a new one; verify against `models/im_alert.py`'s `_run_low_stock_scan` and the responsible-user/fallback-user activity logic.
- [x] 3.5 Write `docs/guide/07-stock-report.md`: where the print action lives on a warehouse record, what's excluded (zero-stock products), reading the PDF; verify by generating one against demo data and checking the line/total math by hand.

## 4. MCP connector, as a non-developer

- [x] 4.1 Write `docs/guide/08-mcp-setup.md`: installing `im_mcp`, generating an API key, the MCP User vs. MCP Admin distinction in depth, creating a connector, enabling models in Access Rules (and that it's global, not per-connector) — with a troubleshooting note for the exact "not allowed to 'x' on 'y'" error and what it means; verify every UI path against the shipped views (`im_mcp_connector_views.xml`, `im_mcp_access_views.xml`).
- [x] 4.2 Write `docs/guide/09-mcp-connect.md`: the `.mcp.json` (Claude Code) and `claude_desktop_config.json` (Claude Desktop via `mcp-remote`) examples, reused byte-for-byte (content-identical) from README's MCP connector section — not reinvented — plus the `mcp-remote` stale-OAuth-cache troubleshooting note also already in README; verify both JSON blocks match README's with a diff, not just by eye.
- [x] 4.3 Write `docs/guide/10-mcp-usage.md`: several concrete example prompts across different tools (not just search), what kind of response to expect for each, and how to read a refusal message; verify by actually running at least two different prompts against the live Docker instance and pasting the real responses.

## 5. Wire it up

- [x] 5.1 Add a one-line pointer near the top of `README.md` ("New to the app? See [GUIDE.md](GUIDE.md) for a task-by-task walkthrough.") — no other README restructuring; verify the link resolves.
- [x] 5.2 Proofread pass: every UI label, button name, and menu path mentioned across all `docs/guide/*.md` pages matches what's actually in the running app — verified against view/model source (`im_*_views.xml`, `reports/im_stock_report.xml`, `ir.actions.report`'s binding mechanism, `res.users` API-key wizard source) and 3 live calls against the running Docker instance (`search_records` on `im.alert`/`im.purchase.order`, `draft_stock_move`, cleaned up the test move afterward). No drift found; no full browser click-through done (would need the user's explicit go-ahead per their global Chrome-automation rule).
