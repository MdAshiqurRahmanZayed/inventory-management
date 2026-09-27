from odoo import fields
from odoo import models


class ImProductCategory(models.Model):
    _name = "im.product.category"
    _description = "Product Category"
    _order = "name"

    name = fields.Char(required=True)
