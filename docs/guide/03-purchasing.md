# Purchasing

**Purchasing > Purchase Orders.** This is how stock enters the system from a supplier.

## Before you start

You need a supplier contact (role "Supplier" or "Both") and at least one product already created. If either doesn't exist yet, create the contact under **Contacts** and the product under **Products** first — the order form won't let you type a free-text supplier or product name, only pick an existing record.

## The lifecycle

A purchase order moves through four states. Each transition is a button on the order form, and each button only appears when it's actually a valid next step (you won't see "Receive All" on a Draft order, for instance).

### 1. Create (Draft)

New order, pick the supplier and the warehouse the goods are going to, add one or more lines (product + quantity). Saved as Draft automatically — nothing has committed yet, and you can edit freely.

**Who can do this:** Stock User or Manager.

### 2. Confirm

Click **Confirm**. This is the one step restricted to a **Stock Manager only** — a Stock User can prepare an order (pick everything, add every line) but can't commit the spend themselves. If you're a Stock User and the Confirm button is greyed out or missing, that's not a bug — ask a Manager to confirm it.

Confirming doesn't move any stock yet; it just locks the order in as committed.

### 3. Receive All

Once the goods physically arrive, click **Receive All**. This creates the actual stock moves (one per order line) and marks them Done — quantity-on-hand at the warehouse's default receiving location goes up right then, visible immediately on the dashboard and the product's own record.

**Who can do this:** Stock User or Manager.

### 4. Mark Done

Closes the order out. Once Done, the order (and its moves) are locked — not even a Manager can edit a Done move afterward.

### Cancel

Available any time before Done. A cancelled order doesn't count toward the dashboard's Open Orders tile and no stock moves are created for it.

## What to expect at each step

| After you... | Stock changes? | Order shows as |
| --- | --- | --- |
| Create + save | No | Draft |
| Confirm | No | Confirmed |
| Receive All | **Yes — quantity-on-hand increases** | Confirmed (moves now Done) |
| Mark Done | No further change | Done |

## Troubleshooting

**"I can't find the Confirm button" / "It's there but nothing happens."** You're very likely logged in as a Stock User, not a Manager — confirming is deliberately Manager-only so a User can't commit spending on their own. Check your role (see **01-roles.md**) and ask a Manager to confirm the order if that's the case.

**"I received the order but the dashboard's stock value didn't change."** Give it a moment and refresh — `stock_value` recomputes automatically off the move going Done, but the dashboard widget itself only re-fetches when you reload it.
