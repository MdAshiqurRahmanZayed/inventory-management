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

Core models, purchasing, sales, stock moves/quants, and adjustments are
implemented. Role-based access and the MCP connector are still in
progress — see the project README and OpenSpec change history.
""",
    "author": "Ashiqur Zayed",
    "license": "LGPL-3",
    "depends": ["base", "mail"],
    "data": [
        "data/ir_sequence.xml",
        "security/ir.model.access.csv",
        "views/inventory_management_menu.xml",
        "views/im_product_category_views.xml",
        "views/im_product_views.xml",
        "views/res_partner_views.xml",
        "views/im_warehouse_views.xml",
        "views/im_location_views.xml",
        "views/im_purchase_order_views.xml",
        "views/im_move_views.xml",
        "views/im_quant_views.xml",
        "views/im_sale_order_views.xml",
        "views/im_shipment_views.xml",
        "views/im_adjustment_views.xml",
    ],
    "demo": [
        "demo/im_demo_data.xml",
        "demo/im_demo_data_phase3.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "inventory_management/static/src/dashboard/dashboard.js",
            "inventory_management/static/src/dashboard/dashboard.xml",
            "inventory_management/static/src/dashboard/dashboard.scss",
        ],
    },
    "installable": True,
    "application": True,
}
