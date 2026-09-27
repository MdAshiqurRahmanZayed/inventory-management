from odoo import fields
from odoo import models


class ImWarehouse(models.Model):
    _name = "im.warehouse"
    _description = "Warehouse"
    _order = "name"

    name = fields.Char(required=True)
    address = fields.Char()
    capacity = fields.Float()
    email = fields.Char()
    location_ids = fields.One2many("im.location", "warehouse_id", string="Locations")
