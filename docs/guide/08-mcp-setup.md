# MCP Setup

This is what lets an AI assistant (Claude, or any MCP-compatible client) check your stock and draft moves — through the exact same permission system as a human user, nothing bypassed. Setup is a one-time thing per person who wants to connect an assistant; see **09-mcp-connect.md** for actually wiring up a client afterward.

## 1. Install the app (if not already)

**Apps > Update Apps List**, search "Inventory Management MCP Connector." It won't show by default — clear the "Apps" filter chip first, since it's a dependent module (depends on `inventory_management`), not a standalone app Odoo surfaces automatically. Click **Install**.

## 2. Generate yourself an Odoo API key

This is a few more clicks than it first looks, because Odoo makes you re-confirm your identity before handing out a key — that's expected, not an error.

1. Click your avatar (top-right corner) > **My Profile** — or **Settings > Users & Companies > Users** and open your own user record; either gets you to the same place.
2. Open the **Account Security** tab. Under **API Keys**, click **New API Key**.
3. Odoo asks you to **re-enter your login password** ("Security Control" dialog) before it'll let you proceed — this confirms it's really you, not someone who's grabbed an already-open session. Type your password, confirm.
4. A small form appears: **Description** (a name you'll recognize later, e.g. "Claude Desktop key" — required) and **Duration** (1 Day / 1 Week / 1 Month / 3 Months / 6 Months / 1 Year / a custom date, and "Persistent Key" if your role allows it — most non-admin roles won't see the Persistent option, only the capped durations). Pick a duration — if this is just for testing, a short one is safer.
5. Click **Generate Key**.
6. The key appears on screen, in plain text, with a **Copy** button — this is the **only time** it's ever shown. Copy it now and store it somewhere (a password manager, not a sticky note). If you close this dialog without copying it, there's no way to retrieve it again — you'd have to revoke it and generate a new one.

## 3. Get added to the MCP User group

Without this, the endpoint refuses every single call, even with a perfectly valid API key — the group check happens before anything else. On your own user form, under the **MCP Access** privilege row, select **MCP User** (or ask an MCP Admin to do it for you if you can't edit your own groups).

## 4. An MCP Admin creates a connector for you

This step needs someone with the **MCP Admin** role (see **01-roles.md**) — it's not something a plain MCP User can do themselves.

Open the **MCP Connector** app (only visible to MCP Admins — if you're logged in as a plain MCP User, you won't see this app tile at all, which is correct, not a bug). Under **Connectors > New**:
- **Name** — something recognizable, e.g. "Claude Desktop, warehouse lead."
- **User** — set to the person this connector runs as (you, if it's your own).
- **Active** / **Expires on** / **Rate limit** — optional; leave Active checked and the rest blank unless you specifically want an expiry date.

## 5. An MCP Admin enables the models MCP may use

Same app, **Access Rules**. This is the single most important thing to understand about this step: **it's global**, not per-connector. Enabling `im.product` for read here means *every* connector, for *every* user, can read `im.product` — subject still to that connector's own bound user's native permissions (a connector run by a Stock Viewer still can't write, even if the rule allows it). There's no separate "which models can *this* connector see" setting.

For each model you want reachable: tick **Enabled**, then tick whichever of Read/Write/Create/Delete should be allowed. Nothing is reachable at all until a row exists here with Enabled ticked — deny-by-default.

## Troubleshooting

**Error: `MCP is not allowed to 'create' on 'im.product'. Ask a Manager to enable it: MCP Connector app > Access Rules > 'im.product' > tick 'create'.`** This is the system working correctly, not a bug — it's telling you exactly which model/operation needs enabling and where. Pass it to an MCP Admin.

**"I did everything above but it still refuses my calls."** Check, in order: (1) is the API key actually valid and not expired/revoked, (2) are you actually in the MCP User group — check your own user form, (3) does a connector exist with `user_id` set to you, and is it Active and not past its expiry date, (4) is the model you're calling actually enabled in Access Rules. Any one of these missing causes a refusal with no partial success.

**"The MCP Connector app tile isn't showing up for me at all."** You're not an MCP Admin — that's by design; a plain MCP User never sees the configuration screens, only an AI assistant connecting through their account does.
