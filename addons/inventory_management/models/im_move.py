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
IMMUTABLE_ON_DONE_FIELDS = {"product_id", "quantity", "source_id", "dest_id"}


class ImMove(models.Model):
    _name = "im.move"
    _description = "Stock Move"
    _order = "id desc"
    _rec_name = "name"

    name = fields.Char(
        string="Move",
        compute="_compute_name",
        store=True,
    )
    number = fields.Char(
        string="SM Number",
        readonly=True,
        default=lambda self: self.env["ir.sequence"].next_by_code("im.move"),
    )
    product_id = fields.Many2one("im.product", string="Product", required=True)
    quantity = fields.Float(required=True)
    source_id = fields.Many2one("im.location", string="Source Location")
    dest_id = fields.Many2one("im.location", string="Destination Location")
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
    done_date = fields.Datetime(readonly=True)
    user_id = fields.Many2one("res.users", string="Done By", readonly=True)
    purchase_line_id = fields.Many2one("im.purchase.line", string="Purchase Line")

    @api.depends("number", "product_id", "quantity")
    def _compute_name(self):
        for record in self:
            if record.number and record.product_id:
                record.name = f"{record.number} {record.product_id.name} x{record.quantity}"
            else:
                record.name = "New"

    @api.constrains("source_id", "dest_id")
    def _check_has_a_location(self):
        for move in self:
            if not move.source_id and not move.dest_id:
                raise ValidationError(
                    "A stock move needs at least a source or a destination location."
                )

    @api.model_create_multi
    def create(self, vals_list):
        moves = super().create(vals_list)
        moves._check_has_a_location()
        return moves

    def write(self, vals):
        if "state" in vals:
            for move in self:
                new_state = vals["state"]
                if new_state == move.state:
                    continue
                allowed = ALLOWED_TRANSITIONS.get(move.state, set())
                if new_state not in allowed:
                    raise ValidationError(
                        f'Stock move cannot go from "{move.state}" to "{new_state}".'
                    )
        if IMMUTABLE_ON_DONE_FIELDS.intersection(vals) and any(
            move.state == "done" for move in self
        ):
            raise ValidationError("A done stock move cannot be edited.")
        result = super().write(vals)
        if vals.get("state") == "done":
            for move in self:
                move._apply_done_stock_effect()
        return result

    def action_confirm(self):
        for move in self:
            move.state = "confirmed"

    def action_done(self):
        for move in self:
            move.state = "done"

    def action_cancel(self):
        for move in self:
            move.state = "cancelled"

    def _apply_done_stock_effect(self):
        self.ensure_one()
        Quant = self.env["im.quant"]
        if self.source_id:
            Quant._apply_move(self.product_id, self.source_id, -self.quantity)
        if self.dest_id:
            Quant._apply_move(self.product_id, self.dest_id, self.quantity)
        self.write({"done_date": fields.Datetime.now(), "user_id": self.env.uid})
