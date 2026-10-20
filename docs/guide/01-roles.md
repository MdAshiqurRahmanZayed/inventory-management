# Roles

There are two independent sets of roles in this app — the core **Stock** roles (who can see/change inventory data) and the **MCP** roles (who can set up or use the AI connector). They don't overlap: having a Stock role doesn't automatically give you an MCP role, and vice versa.

## Stock roles

Each one is a strict superset of the one before it — a Manager automatically has everything a User has, who has everything a Viewer has. Internally this is `implied_ids` in `addons/inventory_management/security/security.xml`: picking Manager silently grants User and Viewer too.

### Stock Viewer

Read-only. Can see products, stock levels, purchase and sale orders, shipments, moves, and the full dashboard. Typical for sales staff or accountants who need to check stock without being able to change anything.

### Stock User

Everything a Viewer can, plus:
- Draft purchase and sales orders (but not confirm a purchase order — that's Manager-only)
- Create shipments, create and confirm stock moves
- Receive purchase orders, deliver sales orders
- Close low-stock alerts
- Edit their own moves while still in Draft (a Done move is locked for everyone, including Managers)

Typical for warehouse and purchasing staff doing day-to-day operations.

### Stock Manager

Everything a User can, plus:
- Confirm a purchase order (committing the spend)
- Create and confirm stock adjustments
- Manage products, categories, suppliers, customers, warehouses, and locations
- Read the full API call log (if `im_mcp` is installed)

Typical for a warehouse lead or anyone responsible for the data model itself, not just moving stock through it.

## MCP roles

Separate privilege, independent of the Stock roles above — see **08-mcp-setup.md** for the full setup flow.

### MCP User

Lets an AI assistant connect *as you* — specifically, it's the gate the `/mcp/` endpoint checks before accepting any call. Without it, every call is refused regardless of API key validity. On its own, it does **not** let you configure anything — you can't see the MCP Connector app, create a connector, or change which models are enabled.

### MCP Admin

Implies MCP User (so an Admin can also connect an assistant as themselves), plus the ability to see and configure the whole MCP Connector app: create/edit connectors, enable or disable models and operations in Access Rules, and read every user's call log (not just their own).

## How to tell which role(s) you have

**Settings > Users & Companies > Users**, open your own user record. Under the "Role" privilege row you'll see which one of Stock Viewer/User/Manager is selected (it's a single choice, like a radio button — picking one implies the ones below it). Under the separate "MCP Access" privilege row, you'll see MCP User or MCP Admin, if either is assigned.

## How a Manager assigns a role

Same screen, on someone else's user record. Only a Stock Manager (for Stock roles) or an MCP Admin (for MCP roles) can change another user's role — a Stock User can't promote themselves or anyone else.
