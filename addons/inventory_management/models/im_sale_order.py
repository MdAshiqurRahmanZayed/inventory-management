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


class ImSaleOrder(models.Model):
    _name = "im.sale.order"
    _description = "Sale Order"
    _order = "order_date desc, id desc"
    _rec_name = "name"

    name = fields.Char(
        string="SO",
        compute="_compute_name",
        store=True,
    )
    number = fields.Char(
        string="SO Number",
        readonly=True,
        default=lambda self: self.env["ir.sequence"].next_by_code("im.sale.order"),
    )
    customer_id = fields.Many2one(
        "res.partner",
        string="Customer",
        required=True,
        domain=[("partner_role", "in", ["customer", "both"])],
    )
    warehouse_id = fields.Many2one("im.warehouse", string="Shipping Warehouse", required=True)
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
    line_ids = fields.One2many("im.sale.line", "order_id", string="Lines")
    shipment_id = fields.Many2one("im.shipment", string="Shipment", readonly=True)

    @api.depends("number", "customer_id", "warehouse_id")
    def _compute_name(self):
        for record in self:
            if record.number and record.customer_id and record.warehouse_id:
                record.name = f"{record.number} {record.customer_id.name}-{record.warehouse_id.name}"
            else:
                record.name = "New"

    @api.depends("line_ids.subtotal")
    def _compute_amount_total(self):
        for order in self:
            order.amount_total = sum(order.line_ids.mapped("subtotal"))

    def write(self, vals):
        if "state" in vals:
            for order in self:
                new_state = vals["state"]
                if new_state == order.state:
                    continue
                allowed = ALLOWED_TRANSITIONS.get(order.state, set())
                if new_state not in allowed:
                    raise ValidationError(
                        f'Sale order cannot go from "{order.state}" to "{new_state}".'
                    )
                if new_state == "done":
                    if not order.shipment_id or any(
                        move.state != "done" for move in order.shipment_id.move_ids
                    ):
                        raise ValidationError(
                            "A sale order can only be marked Done once all of its "
                            "delivery moves are Done."
                        )
        return super().write(vals)

    def action_confirm(self):
        for order in self:
            if order.state != "draft":
                raise ValidationError("Only a Draft sale order can be confirmed.")
            if not order.line_ids:
                raise ValidationError("A sale order needs at least one line to be confirmed.")
            source_location = order.warehouse_id._get_default_shipping_location()
            shipment = self.env["im.shipment"].create(
                {
                    "sale_order_id": order.id,
                    "warehouse_id": order.warehouse_id.id,
                }
            )
            for line in order.line_ids:
                self.env["im.move"].create(
                    {
                        "product_id": line.product_id.id,
                        "quantity": line.quantity,
                        "source_id": source_location.id,
                        "shipment_id": shipment.id,
                    }
                )
            order.shipment_id = shipment
            order.state = "confirmed"
            shipment.status = "confirmed"

    def action_deliver_all(self):
        for order in self:
            if not order.shipment_id:
                raise ValidationError("This order has no shipment to deliver.")
            order.shipment_id.action_deliver_all()

    def action_done(self):
        for order in self:
            order.state = "done"
            if order.shipment_id.status != "done":
                order.shipment_id.status = "done"

    def action_cancel(self):
        for order in self:
            order.state = "cancelled"
