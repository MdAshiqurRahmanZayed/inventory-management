from odoo import api
from odoo import fields
from odoo import models


class ImProduct(models.Model):
    _name = "im.product"
    _description = "Product"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "name"

    _sku_unique = models.Constraint(
        "unique(sku)",
        "SKU must be unique across all products.",
    )

    name = fields.Char(required=True)
    sku = fields.Char(string="SKU", required=True)
    description = fields.Html()
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
    quant_ids = fields.One2many("im.quant", "product_id", string="Quants")
    qty_on_hand = fields.Float(compute="_compute_qty_on_hand", store=True)
    stock_value = fields.Float(compute="_compute_stock_value", store=True)
    responsible_user_id = fields.Many2one(
        "res.users",
        string="Responsible User",
        help="Notified by activity when this product falls below its reorder level.",
    )

    @api.depends("quant_ids.quantity")
    def _compute_qty_on_hand(self):
        quant_groups = self.env["im.quant"]._read_group(
            [("product_id", "in", self.ids)],
            groupby=["product_id"],
            aggregates=["quantity:sum"],
        )
        totals = {product.id: total for product, total in quant_groups}
        for product in self:
            product.qty_on_hand = totals.get(product.id, 0.0)

    @api.depends("qty_on_hand", "cost")
    def _compute_stock_value(self):
        for product in self:
            product.stock_value = product.qty_on_hand * product.cost
