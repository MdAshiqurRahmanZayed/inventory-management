from odoo import fields
from odoo import models


class ImProduct(models.Model):
    _name = "im.product"
    _description = "Product"
    _order = "name"

    _sku_unique = models.Constraint(
        "unique(sku)",
        "SKU must be unique across all products.",
    )

    name = fields.Char(required=True)
    sku = fields.Char(string="SKU", required=True)
    description = fields.Text()
    category_id = fields.Many2one("im.product.category", string="Category", required=True)
    uom = fields.Char(string="Unit of Measure")
    cost = fields.Float()
    sale_price = fields.Float()
    reorder_level = fields.Float()
    supplier_id = fields.Many2one(
        "res.partner",
        string="Supplier",
        domain=[("partner_role", "in", ["supplier", "both"])],
    )
    qty_on_hand = fields.Float(default=0.0)
