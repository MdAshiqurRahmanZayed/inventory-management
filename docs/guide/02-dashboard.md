# Dashboard

Click the **Inventory Management** app tile — you land here. It's the first thing anyone sees, so here's what every number actually means.

## The count tiles

| Tile | What it counts |
| --- | --- |
| Products | Every `im.product` record, period — no filtering |
| Categories | Every `im.product.category` record |
| Warehouses | Every `im.warehouse` record |
| Locations | Every `im.location` record, across all warehouses |
| Suppliers | Contacts with partner role "Supplier" or "Both" |
| Customers | Contacts with partner role "Customer" or "Both" |

These are plain `search_count([])` totals — if a count looks wrong, it's because a record genuinely exists (or doesn't), not a filtering bug.

## Stock Value (highlighted tile)

Sum, across **every** product and **every** location, of quantity-on-hand × cost. This is a stored, always-up-to-date field (`im.product.stock_value`) — it recomputes automatically the instant a move goes Done or a product's cost changes, no manual refresh needed. On a brand-new install with no stock received yet, this is 0.

## Low Stock (warning tile)

How many products currently have an **open** low-stock alert (see **06-alerts.md**). Closing an alert for a restocked product removes it from this count immediately; the count does **not** mean "products below reorder level right now" — it's specifically "alerts nobody has closed yet," which is usually the same thing but can drift if someone restocks without closing the alert.

## Open Orders

Purchase orders + sale orders currently in **Draft** or **Confirmed** state. Once an order is **Done** or **Cancelled**, it drops out of this count. A Draft order you never confirmed still counts — "open" here means "not yet finished," not "actively being worked."

## Charts

- **Products by Category** — pie chart, one slice per category, by product count.
- **Contacts by Role** — pie chart, Supplier / Customer / Both.
- **Moves in the Last 7 Days** — bar chart, broken into receipts / deliveries / adjustments / plain transfers. Only **Done** moves count, and only within the last 7 days (configurable — see below). A move still in Draft or Confirmed never shows up here, no matter how old.

## Top Movers (30 Days)

A ranked list (top 5 max) of products by total quantity moved in the last 30 days, across all Done moves. If fewer than 5 products had any movement, the list just shows however many there are — it's never padded with fake zero-value entries to fill out 5 slots. If nothing moved in the window, the list says so plainly instead of showing an empty chart.

## Changing the time windows

Both the 7-day (recent moves) and 30-day (top movers) windows are configurable system parameters, not hardcoded — a developer can change them under **Settings > Technical > System Parameters**: `inventory_management.recent_moves_window_days` and `inventory_management.top_movers_window_days`. Day-to-day users won't normally need to touch these.
