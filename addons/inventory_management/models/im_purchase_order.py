from odoo import api
from odoo import fields
from odoo import models
from odoo.exceptions import ValidationError

ALLOWED_TRANSITIONS = {
    "draft": {"confirmed", "cancelled"},
    "confirmed": {"done", "cancelled"},
    "done": set(),
    "cancelled": set(),
}


class ImPurchaseOrder(models.Model):
    _name = "im.purchase.order"
    _description = "Purchase Order"
    _order = "order_date desc, id desc"

    supplier_id = fields.Many2one(
        "res.partner",
        string="Supplier",
        required=True,
        domain=[("partner_role", "in", ["supplier", "both"])],
    )
    warehouse_id = fields.Many2one("im.warehouse", string="Receiving Warehouse", required=True)
    order_date = fields.Date(default=fields.Date.context_today)
    expected_date = fields.Date()
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("confirmed", "Confirmed"),
            ("done", "Done"),
            ("cancelled", "Cancelled"),
        ],
        required=True,
        default="draft",
    )
    amount_total = fields.Float(compute="_compute_amount_total", store=True)
    line_ids = fields.One2many("im.purchase.line", "order_id", string="Lines")
    move_ids = fields.One2many(
        "im.move", string="Moves", compute="_compute_move_ids"
    )

    @api.depends("line_ids.subtotal")
    def _compute_amount_total(self):
        for order in self:
            order.amount_total = sum(order.line_ids.mapped("subtotal"))

    @api.depends("line_ids.move_ids")
    def _compute_move_ids(self):
        for order in self:
            order.move_ids = order.line_ids.move_ids

    def write(self, vals):
        if "state" in vals:
            for order in self:
                new_state = vals["state"]
                if new_state == order.state:
                    continue
                allowed = ALLOWED_TRANSITIONS.get(order.state, set())
                if new_state not in allowed:
                    raise ValidationError(
                        f'Purchase order cannot go from "{order.state}" to "{new_state}".'
                    )
                if new_state == "done":
                    moves = self.env["im.move"].search(
                        [("purchase_line_id", "in", order.line_ids.ids)]
                    )
                    if any(move.state != "done" for move in moves):
                        raise ValidationError(
                            "A purchase order can only be marked Done once all of "
                            "its receipt moves are Done."
                        )
        return super().write(vals)

    def action_confirm(self):
        for order in self:
            if order.state != "draft":
                raise ValidationError("Only a Draft purchase order can be confirmed.")
            if not order.line_ids:
                raise ValidationError("A purchase order needs at least one line to be confirmed.")
            dest_location = order.warehouse_id._get_default_receiving_location()
            for line in order.line_ids:
                self.env["im.move"].create(
                    {
                        "product_id": line.product_id.id,
                        "quantity": line.quantity,
                        "dest_id": dest_location.id,
                        "purchase_line_id": line.id,
                    }
                )
            order.state = "confirmed"

    def action_receive_all(self):
        for order in self:
            if order.state != "confirmed":
                raise ValidationError("Only a Confirmed purchase order can receive moves.")
            for move in order.move_ids:
                if move.state == "draft":
                    move.write({"state": "confirmed"})
                if move.state == "confirmed":
                    move.write({"state": "done"})

    def action_done(self):
        for order in self:
            order.state = "done"

    def action_cancel(self):
        for order in self:
            order.state = "cancelled"
