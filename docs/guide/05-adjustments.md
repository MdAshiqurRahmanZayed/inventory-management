# Stock Adjustments

**Inventory > Stock Adjustments.** Use this when a physical count doesn't match what the system thinks is there — damage, shrinkage, a miscount on the last stock-take, found stock that was never logged. It's **not** how you'd normally move stock in or out (that's purchasing and sales, with their own paper trail) — an adjustment is specifically the "something's wrong, here's the correction" tool, and every one of them is kept as a permanent audit record.

## Who can create one

**Stock Manager only.** A Stock Viewer can't see adjustments at all; a Stock User can see them but can't create or confirm one. This is deliberate — adjustments bypass the normal order-and-delivery paper trail, so creating one is restricted to the role responsible for the data being accurate.

## Creating one

Pick:
- **Product**
- **Location** — which specific location's stock you're correcting
- **Type** — Increase or Decrease
- **Quantity**
- **Reason** — a free-text field, and it's **required**. There is no way to save an adjustment without filling this in; it's what makes the audit trail actually useful later ("why did this change?"), not just a number with no explanation.

Click **Confirm** to apply it — this creates the underlying stock move and updates quantity-on-hand immediately, same as any other Done move.

## What to expect

| After you... | Stock changes? |
| --- | --- |
| Create + save (before Confirm) | No |
| Confirm | **Yes — quantity-on-hand changes by the amount specified, immediately** |

Once confirmed, the adjustment (and its underlying move) is locked, same as any other Done move — not even a Manager can edit it afterward. If you got the quantity wrong, create a second, opposite adjustment to correct it, with its own reason explaining the correction — don't try to edit history.

## Troubleshooting

**"I can't find Stock Adjustments in the menu at all."** You're a Stock Viewer — adjustments aren't visible to that role. Ask a Manager, or check your own role (**01-roles.md**).

**"I can see the list but there's no way to create a new one."** You're a Stock User — you have read access but not create access. Same fix: a Manager needs to do it, or promote your role if that's appropriate.

**"It won't let me save."** Check the Reason field — it's the most common blocker, since it's the one field that's easy to skip and the system won't let you save without it.
