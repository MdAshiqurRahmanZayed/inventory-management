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


class ImShipment(models.Model):
    _name = "im.shipment"
    _description = "Shipment"
    _order = "id desc"
    _rec_name = "name"

    name = fields.Char(
        string="Shipment",
        compute="_compute_name",
        store=True,
    )
    number = fields.Char(
        string="Shipment Number",
        readonly=True,
        default=lambda self: self.env["ir.sequence"].next_by_code("im.shipment"),
    )
    sale_order_id = fields.Many2one("im.sale.order", string="Sale Order", required=True)
    warehouse_id = fields.Many2one("im.warehouse", string="Warehouse")
    shipment_date = fields.Date(default=fields.Date.context_today)
    status = fields.Selection(
        [
            ("draft", "Draft"),
            ("confirmed", "Confirmed"),
            ("done", "Done"),
            ("cancelled", "Cancelled"),
        ],
        required=True,
        default="draft",
    )
    move_ids = fields.One2many("im.move", "shipment_id", string="Moves")

    @api.depends("number", "sale_order_id")
    def _compute_name(self):
        for record in self:
            if record.number and record.sale_order_id:
                record.name = f"{record.number} {record.sale_order_id.name}"
            else:
                record.name = "New"

    def write(self, vals):
        if "status" in vals:
            for shipment in self:
                new_status = vals["status"]
                if new_status == shipment.status:
                    continue
                allowed = ALLOWED_TRANSITIONS.get(shipment.status, set())
                if new_status not in allowed:
                    raise ValidationError(
                        f'Shipment cannot go from "{shipment.status}" to "{new_status}".'
                    )
                if new_status == "done":
                    if any(move.state != "done" for move in shipment.move_ids):
                        raise ValidationError(
                            "A shipment can only be marked Done once all of its "
                            "delivery moves are Done."
                        )
        return super().write(vals)

    def action_deliver_all(self):
        for shipment in self:
            if shipment.status != "confirmed":
                raise ValidationError("Only a Confirmed shipment can deliver moves.")
            for move in shipment.move_ids:
                if move.state == "draft":
                    move.write({"state": "confirmed"})
                if move.state == "confirmed":
                    move.write({"state": "done"})

    def action_done(self):
        for shipment in self:
            shipment.status = "done"

    def action_cancel(self):
        for shipment in self:
            shipment.status = "cancelled"
