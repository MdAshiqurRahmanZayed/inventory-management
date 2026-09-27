from odoo import fields
from odoo import models


class ImWelcome(models.TransientModel):
    _name = "im.welcome"
    _description = "Inventory Management Welcome Screen"

    message = fields.Html(readonly=True, default=(
        "<p><strong>Inventory Management</strong> is scaffolded and running, "
        "with no business features yet.</p>"
        "<p>Products, orders, stock moves, roles, the dashboard, and the MCP "
        "connector land in upcoming changes.</p>"
    ))
