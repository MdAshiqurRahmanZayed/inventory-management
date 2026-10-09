from odoo import api
from odoo import fields
from odoo import models
from odoo.exceptions import ValidationError


class ImQuant(models.Model):
    _name = "im.quant"
    _description = "Stock Quant"
    _order = "id"

    _product_location_unique = models.Constraint(
        "unique(product_id, location_id)",
        "Only one quant row is allowed per product/location pair.",
    )

    product_id = fields.Many2one("im.product", string="Product", required=True)
    location_id = fields.Many2one("im.location", string="Location", required=True)
    quantity = fields.Float(default=0.0)

    def _apply_move(self, product, location, delta):
        quant = self.search(
            [("product_id", "=", product.id), ("location_id", "=", location.id)],
            limit=1,
        )
        new_quantity = (quant.quantity if quant else 0.0) + delta
        if location.type == "internal" and new_quantity < 0:
            raise ValidationError(
                f'Stock move would take "{product.name}" below zero at '
                f'location "{location.name}".'
            )
        allowed_self = self.sudo().with_context(im_allow_quant_write=True)
        if quant:
            allowed_self.browse(quant.id).write({"quantity": new_quantity})
        else:
            allowed_self.create(
                {
                    "product_id": product.id,
                    "location_id": location.id,
                    "quantity": new_quantity,
                }
            )

    @api.model_create_multi
    def create(self, vals_list):
        if not self.env.context.get("im_allow_quant_write"):
            raise ValidationError(
                "Stock quants cannot be created directly; they change only "
                "when a stock move reaches Done."
            )
        return super().create(vals_list)

    def write(self, vals):
        if not self.env.context.get("im_allow_quant_write"):
            raise ValidationError(
                "Stock quants cannot be edited directly; they change only "
                "when a stock move reaches Done."
            )
        return super().write(vals)
