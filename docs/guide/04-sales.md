# Sales

**Sales > Sale Orders.** This is how stock leaves the system to a customer.

## Before you start

You need a customer contact (role "Customer" or "Both"), an existing product, and — unlike purchasing — some stock already on hand at the warehouse you're selling from. You can't deliver more than what's actually there.

## The lifecycle

### 1. Create (Draft)

Pick the customer and warehouse, add lines (product + quantity). Saved as Draft, fully editable.

**Who can do this:** Stock User or Manager.

### 2. Confirm

Click **Confirm**. Unlike a purchase order, this step is **not** Manager-restricted — any Stock User can confirm a sale order. Confirming automatically creates a shipment behind the scenes (you'll see it referenced on the order, and separately under its own shipment record) — this represents the physical delivery that's about to happen.

### 3. Deliver All

Click **Deliver All** once the goods are ready to go out. This creates the stock moves and marks them Done — quantity-on-hand at the relevant location decreases immediately.

If you try to deliver more than what's on hand, the system blocks it — you can't go negative. Receive more stock first (see **03-purchasing.md**), or reduce the order line's quantity.

### 4. Mark Done

Closes the order out, same as purchasing — once Done, nothing on it can be edited, by anyone.

### Cancel

Available any time before Done, same as purchasing.

## What to expect at each step

| After you... | Stock changes? | Order shows as |
| --- | --- | --- |
| Create + save | No | Draft |
| Confirm | No (but a shipment record is created) | Confirmed |
| Deliver All | **Yes — quantity-on-hand decreases** | Confirmed (moves now Done) |
| Mark Done | No further change | Done |

## Troubleshooting

**"Deliver All" did nothing / gave an error.** Most likely there isn't enough stock on hand for one of the lines. Check the product's `qty_on_hand` (its own record, or the dashboard) before trying again — you may need to receive a purchase order first.

**"I confirmed but nothing shipped yet."** That's expected — confirming only creates the shipment record and locks the order in; the actual stock movement happens on **Deliver All**, a separate, deliberate step.
