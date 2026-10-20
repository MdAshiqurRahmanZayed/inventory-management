{
    "name": "Inventory Management MCP Connector",
    "version": "19.0.1.0.0",
    "category": "Inventory",
    "summary": "Native MCP server exposing inventory_management to AI assistants.",
    "description": """
        Inventory Management MCP Connector
        ===================================

        Exposes a `POST /mcp/` JSON-RPC endpoint (MCP streamable-HTTP transport)
        inside Odoo itself — no separate server process. Each connector runs as
        a real Odoo user, authenticated by that user's own Odoo API key. Global,
        per-model access rules sit on top of each user's native Odoo permissions
        (never bypassed), with generic record tools, a stock-move drafting tool,
        and a full audit log of every call.
    """,
    "author": "Ashiqur Zayed",
    "license": "LGPL-3",
    "depends": ["base", "inventory_management"],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "security/rules.xml",
        "views/im_mcp_connector_views.xml",
        "views/im_mcp_access_views.xml",
        "views/im_api_log_views.xml",
    ],
    "installable": True,
    "application": True,
}
