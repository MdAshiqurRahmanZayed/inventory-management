from odoo import api
from odoo import fields
from odoo import models
from odoo.exceptions import ValidationError


class ImSaleLine(models.Model):
    _name = "im.sale.line"
    _description = "Sale Order Line"
    _rec_name = "name"

    name = fields.Char(
        string="Line",
        compute="_compute_name",
        store=True,
    )
    order_id = fields.Many2one("im.sale.order", string="Order", required=True, ondelete="cascade")
    product_id = fields.Many2one("im.product", string="Product", required=True)
    quantity = fields.Float(required=True)
    unit_price = fields.Float()
    subtotal = fields.Float(compute="_compute_subtotal", store=True)

    @api.depends("order_id", "product_id", "quantity")
    def _compute_name(self):
        for record in self:
            if record.order_id and record.product_id:
                record.name = f"{record.order_id.name} - {record.product_id.name} x{record.quantity}"
            else:
                record.name = "New"

    @api.depends("quantity", "unit_price")
    def _compute_subtotal(self):
        for line in self:
            line.subtotal = line.quantity * line.unit_price

    @api.constrains("quantity")
    def _check_quantity_positive(self):
        for line in self:
            if line.quantity <= 0:
                raise ValidationError("A sale line's quantity must be greater than zero.")
