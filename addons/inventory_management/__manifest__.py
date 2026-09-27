{
    "name": "Inventory Management",
    "version": "19.0.1.0.0",
    "category": "Inventory",
    "summary": "Custom inventory management app: products, orders, stock moves and an MCP-safe API.",
    "description": """
Inventory Management
=====================

A standalone Odoo inventory app covering products, suppliers/customers,
warehouses, purchase and sales orders, stock moves, adjustments and
low-stock alerts, with an OWL dashboard.

This module is currently in an early scaffold state (no business logic
yet). See the project README and OpenSpec change history for progress.
""",
    "author": "Ashiqur Zayed",
    "license": "LGPL-3",
    "depends": ["base", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "views/inventory_management_menu.xml",
    ],
    "installable": True,
    "application": True,
}
