from odoo import api
from odoo import fields
from odoo import models
from odoo.exceptions import ValidationError


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
    is_default_receiving = fields.Boolean(string="Default Receiving Location")

    @api.constrains("is_default_receiving", "type")
    def _check_default_receiving_is_internal(self):
        for location in self:
            if location.is_default_receiving and location.type != "internal":
                raise ValidationError(
                    "Only an internal location can be marked as the default receiving location."
                )
