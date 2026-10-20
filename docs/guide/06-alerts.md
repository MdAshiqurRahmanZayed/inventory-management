# Low-Stock Alerts

**Inventory > Low Stock Alerts.**

## How an alert gets created

A background job runs once a day and checks every product that has a reorder level set. If a product's quantity-on-hand has dipped below its reorder level, an alert opens automatically — you don't create these yourself, and there's no manual "check now" button for a regular user. The alert records a snapshot of the quantity-on-hand at the moment it was raised, so you can see how bad the shortage was even after more stock arrives later.

At the same time, an activity ("to-do") is posted so a real person notices it: it goes to the product's own **Responsible User** field if one is set, or a configured fallback user otherwise. It shows up in that person's activity list/To-Do, the same way any other Odoo activity would.

## Avoiding duplicate alerts

If a product is already sitting on an **open** alert, the daily job won't open a second one for it — you'll only ever have one open alert per product at a time, no matter how many days it stays low.

## Closing an alert

Open the alert, click **Close**. This just marks that specific alert resolved — it doesn't check whether the product is actually restocked, so close it once you've confirmed the stock situation is handled, not just because it's annoying to see on the dashboard.

## What re-triggers a new one

Once closed, if the same product dips below its reorder level **again** on some future day, a brand-new alert opens — closing doesn't "snooze" it forever, it just clears the current instance.

## Where you'll see this reflected elsewhere

- Dashboard's **Low Stock** tile counts open alerts only (see **02-dashboard.md**) — closing one here drops that count immediately.
- The responsible user's own activity list, until they mark the activity done (separately from closing the alert itself — closing the alert and completing the activity are two different actions).

## Troubleshooting

**"A product is clearly low but no alert exists."** Check it actually has a reorder level set above 0 — a product with no reorder level configured is never checked by the daily job at all, by design (there's nothing to compare against).

**"I closed an alert but it's still showing in the dashboard count."** Refresh the dashboard — same as other tiles, it only re-fetches on reload, not live.
