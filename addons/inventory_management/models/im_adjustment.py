from odoo import api
from odoo import fields
from odoo import models
from odoo.exceptions import ValidationError

IMMUTABLE_ON_CONFIRMED_FIELDS = {"product_id", "location_id", "adjustment_type", "quantity"}


class ImAdjustment(models.Model):
    _name = "im.adjustment"
    _description = "Stock Adjustment"
    _order = "date desc, id desc"

    product_id = fields.Many2one("im.product", string="Product", required=True)
    location_id = fields.Many2one(
        "im.location",
        string="Location",
        required=True,
        domain=[("type", "=", "internal")],
    )
    adjustment_type = fields.Selection(
        [("increase", "Increase"), ("decrease", "Decrease")],
        required=True,
        default="increase",
    )
    quantity = fields.Float(required=True)
    reason = fields.Text(required=True)
    user_id = fields.Many2one("res.users", string="User", default=lambda self: self.env.uid)
    date = fields.Datetime(default=fields.Datetime.now)
    state = fields.Selection(
        [("draft", "Draft"), ("confirmed", "Confirmed")],
        required=True,
        default="draft",
    )
    move_ids = fields.One2many("im.move", "adjustment_id", string="Moves")

    @api.constrains("quantity")
    def _check_quantity_positive(self):
        for adjustment in self:
            if adjustment.quantity <= 0:
                raise ValidationError("An adjustment's quantity must be greater than zero.")

    def write(self, vals):
        if IMMUTABLE_ON_CONFIRMED_FIELDS.intersection(vals) and any(
            adjustment.state == "confirmed" for adjustment in self
        ):
            raise ValidationError("A confirmed adjustment cannot be edited.")
        return super().write(vals)

    def action_confirm(self):
        for adjustment in self:
            if adjustment.state != "draft":
                raise ValidationError("Only a Draft adjustment can be confirmed.")
            if adjustment.adjustment_type == "increase":
                move_vals = {
                    "source_id": False,
                    "dest_id": adjustment.location_id.id,
                }
            else:
                move_vals = {
                    "source_id": adjustment.location_id.id,
                    "dest_id": False,
                }
            move = self.env["im.move"].create(
                {
                    "product_id": adjustment.product_id.id,
                    "quantity": adjustment.quantity,
                    "adjustment_id": adjustment.id,
                    **move_vals,
                }
            )
            move.write({"state": "confirmed"})
            move.write({"state": "done"})
            adjustment.state = "confirmed"
