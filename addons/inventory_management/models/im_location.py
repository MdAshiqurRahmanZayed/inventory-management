from odoo import fields
from odoo import models


class ImLocation(models.Model):
    _name = "im.location"
    _description = "Location"
    _order = "name"

    name = fields.Char(required=True)
    warehouse_id = fields.Many2one("im.warehouse", string="Warehouse", required=True)
    type = fields.Selection(
        [("internal", "Internal"), ("vendor", "Vendor"), ("customer", "Customer")],
        required=True,
        default="internal",
    )
    zone_bin = fields.Char(string="Zone / Bin")
