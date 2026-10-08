import logging

from odoo import api
from odoo import fields
from odoo import models

_logger = logging.getLogger(__name__)

FALLBACK_USER_PARAM = "inventory_management.low_stock_fallback_user_id"


class ImAlert(models.Model):
    _name = "im.alert"
    _description = "Low Stock Alert"
    _order = "create_date desc"
    _rec_name = "name"

    name = fields.Char(compute="_compute_name", store=True)
    product_id = fields.Many2one("im.product", string="Product", required=True)
    level = fields.Float(
        string="Quantity on Hand at Alert Time",
        help="Snapshot of the product's quantity on hand when the alert was raised.",
    )
    state = fields.Selection(
        [("open", "Open"), ("closed", "Closed")],
        required=True,
        default="open",
    )

    @api.depends("product_id")
    def _compute_name(self):
        for alert in self:
            alert.name = f"Low stock: {alert.product_id.name}" if alert.product_id else "New"

    def action_close(self):
        self.write({"state": "closed"})

    @api.model
    def _run_low_stock_scan(self):
        """Flag active products below their reorder level, one open alert each."""
        products = self.env["im.product"].search([("reorder_level", ">", 0)])
        low_stock_products = products.filtered(
            lambda product: product.qty_on_hand < product.reorder_level
        )
        if not low_stock_products:
            return
        existing_open = self.search(
            [("product_id", "in", low_stock_products.ids), ("state", "=", "open")]
        )
        already_alerted_ids = set(existing_open.product_id.ids)
        fallback_user = self._get_fallback_user()
        for product in low_stock_products:
            if product.id in already_alerted_ids:
                continue
            alert = self.create(
                {"product_id": product.id, "level": product.qty_on_hand, "state": "open"}
            )
            alert._notify_responsible(fallback_user)

    def _get_fallback_user(self):
        user_id = self.env["ir.config_parameter"].sudo().get_param(FALLBACK_USER_PARAM)
        return self.env["res.users"].browse(int(user_id)).exists() if user_id else self.env["res.users"]

    def _notify_responsible(self, fallback_user):
        self.ensure_one()
        assignee = self.product_id.responsible_user_id or fallback_user
        if not assignee:
            _logger.info(
                "Low-stock alert for %s has no responsible user and no fallback configured; "
                "alert created without an activity.",
                self.product_id.display_name,
            )
            return
        self.product_id.activity_schedule(
            "mail.mail_activity_data_todo",
            summary="Low stock alert",
            note=f"{self.product_id.display_name} is below its reorder level.",
            user_id=assignee.id,
        )
