# Using the MCP Connector

Once connected (**09-mcp-connect.md**), plain-English prompts work — Claude discovers the available tools and models on its own; you don't need to know any JSON-RPC underneath. Below are real example prompts, and the kind of thing they actually return, captured live against a real instance of this app.

## "What's low on stock right now?"

Claude calls `search_records` against `im.alert` filtered to open alerts. A real response looked like this (trimmed to a few rows):

```json
{
  "records": [
    {"id": 19, "product_id": [4, "27-inch Monitor"], "level": 0.0},
    {"id": 20, "product_id": [3, "Mechanical Keyboard"], "level": 0.0},
    {"id": 21, "product_id": [94, "Product for Category Test product category"], "level": 0.0}
  ],
  "count": 10
}
```
Claude would summarize this in prose ("10 products are currently low on stock, including 27-inch Monitor and Mechanical Keyboard...") rather than dumping raw JSON at you — this is just what's actually happening underneath.

## "Show me our open purchase orders."

Claude calls `search_records` against `im.purchase.order` filtered to Draft/Confirmed:
```json
{
  "records": [
    {"id": 18, "name": "PO-0017 Alpha Components Ltd-Main Warehouse", "supplier_id": [42, "Alpha Components Ltd"], "state": "draft"},
    {"id": 3, "name": "New", "supplier_id": [43, "Bengal Office Supply Co"], "state": "draft"},
    {"id": 1, "name": "New", "supplier_id": [42, "Alpha Components Ltd"], "state": "draft"}
  ],
  "count": 3
}
```

## "Draft a stock move for 10 units of the Ergonomic Office Chair into the Main Warehouse."

Claude figures out the product's id and the warehouse's default receiving location on its own (usually by calling `search_records` first to look them up), then calls `draft_stock_move`:
```json
{"id": 451, "state": "draft"}
```
This creates a real `im.move` record — but only in **Draft** state, same as if a human had typed it in by hand. It still needs confirming and receiving/delivering through the normal UI (**03-purchasing.md** / **04-sales.md**) or another MCP call with write access — asking Claude to draft a move never silently moves stock on its own.

## Reading a refusal

If something's not enabled, the error names exactly what's missing:
```json
{"error": {"code": -32001, "message": "MCP is not allowed to 'create' on 'im.product'. Ask a Manager to enable it: MCP Connector app > Access Rules > 'im.product' > tick 'create'."}}
```
Pass that message along to an MCP Admin rather than trying to work around it — it's telling you precisely which model/operation to enable and where (see **08-mcp-setup.md**).

## A few more prompts worth trying

- *"List every warehouse and how many locations each has."*
- *"Which products have no supplier assigned?"*
- *"What moved the most in the last 30 days?"* (mirrors the dashboard's own Top Movers widget, see **02-dashboard.md**)
