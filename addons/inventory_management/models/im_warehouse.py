from odoo import api
from odoo import fields
from odoo import models
from odoo.exceptions import ValidationError


class ImWarehouse(models.Model):
    _name = "im.warehouse"
    _description = "Warehouse"
    _order = "name"

    name = fields.Char(required=True)
    address = fields.Char()
    capacity = fields.Float()
    email = fields.Char()
    location_ids = fields.One2many("im.location", "warehouse_id", string="Locations")
    default_receiving_location_id = fields.Many2one(
        "im.location",
        string="Default Receiving Location",
        compute="_compute_default_receiving_location_id",
    )
    default_shipping_location_id = fields.Many2one(
        "im.location",
        string="Default Shipping Location",
        compute="_compute_default_shipping_location_id",
    )

    @api.depends("location_ids.is_default_receiving")
    def _compute_default_receiving_location_id(self):
        for warehouse in self:
            warehouse.default_receiving_location_id = warehouse.location_ids.filtered(
                "is_default_receiving"
            )[:1]

    @api.depends("location_ids.is_default_shipping")
    def _compute_default_shipping_location_id(self):
        for warehouse in self:
            warehouse.default_shipping_location_id = warehouse.location_ids.filtered(
                "is_default_shipping"
            )[:1]

    def _get_default_receiving_location(self):
        self.ensure_one()
        flagged = self.location_ids.filtered("is_default_receiving")
        if not flagged:
            raise ValidationError(
                f'Warehouse "{self.name}" has no location marked as the default '
                "receiving location. Flag one internal location before confirming "
                "a purchase order against this warehouse."
            )
        if len(flagged) > 1:
            raise ValidationError(
                f'Warehouse "{self.name}" has more than one location marked as '
                "the default receiving location. Only one is allowed."
            )
        return flagged

    def get_stock_report_lines(self):
        """Return (lines, total) for this warehouse's stock report.

        One line per product with positive stock, aggregated across all of
        this warehouse's locations; products with zero stock are excluded.
        """
        self.ensure_one()
        quants = self.env["im.quant"].search(
            [("location_id", "in", self.location_ids.ids), ("quantity", ">", 0)]
        )
        totals_by_product = {}
        for quant in quants:
            totals_by_product[quant.product_id] = (
                totals_by_product.get(quant.product_id, 0.0) + quant.quantity
            )
        lines = [
            {"product": product, "quantity": quantity, "value": quantity * product.cost}
            for product, quantity in totals_by_product.items()
        ]
        lines.sort(key=lambda line: line["product"].name)
        total = sum(line["value"] for line in lines)
        return lines, total

    def _get_default_shipping_location(self):
        self.ensure_one()
        flagged = self.location_ids.filtered("is_default_shipping")
        if not flagged:
            raise ValidationError(
                f'Warehouse "{self.name}" has no location marked as the default '
                "shipping location. Flag one internal location before confirming "
                "a sale order against this warehouse."
            )
        if len(flagged) > 1:
            raise ValidationError(
                f'Warehouse "{self.name}" has more than one location marked as '
                "the default shipping location. Only one is allowed."
            )
        return flagged
