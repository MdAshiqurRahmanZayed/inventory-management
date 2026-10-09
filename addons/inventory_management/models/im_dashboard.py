from datetime import timedelta

from odoo import api
from odoo import fields
from odoo import models

TOP_MOVERS_LIMIT = 5
TOP_MOVERS_WINDOW_DAYS = 30
RECENT_MOVES_WINDOW_DAYS = 7


class ImDashboard(models.AbstractModel):
    _name = "im.dashboard"
    _description = "Inventory Management Dashboard Data"

    @api.model
    def get_dashboard_data(self):
        Product = self.env["im.product"]
        Category = self.env["im.product.category"]
        Warehouse = self.env["im.warehouse"]
        Location = self.env["im.location"]
        Partner = self.env["res.partner"]

        product_by_category = Product._read_group(
            [], groupby=["category_id"], aggregates=["__count"]
        )
        partner_by_role = Partner._read_group(
            [("partner_role", "!=", False)],
            groupby=["partner_role"],
            aggregates=["__count"],
        )

        return {
            "product_count": Product.search_count([]),
            "category_count": Category.search_count([]),
            "warehouse_count": Warehouse.search_count([]),
            "location_count": Location.search_count([]),
            "supplier_count": Partner.search_count(
                [("partner_role", "in", ["supplier", "both"])]
            ),
            "customer_count": Partner.search_count(
                [("partner_role", "in", ["customer", "both"])]
            ),
            "product_by_category": [
                {"label": category.name if category else "Uncategorized", "value": count}
                for category, count in product_by_category
            ],
            "partner_by_role": [
                {"label": role.capitalize(), "value": count}
                for role, count in partner_by_role
            ],
            "stock_value": self._get_stock_value(),
            "low_stock_count": self._get_low_stock_count(),
            "open_orders_count": self._get_open_orders_count(),
            "recent_moves": self._get_recent_moves_breakdown(),
            "top_movers": self._get_top_movers(),
        }

    def _get_stock_value(self):
        quants = self.env["im.quant"].search([])
        return sum(quant.quantity * quant.product_id.cost for quant in quants)

    def _get_low_stock_count(self):
        return self.env["im.alert"].search_count([("state", "=", "open")])

    def _get_open_orders_count(self):
        open_states = ["draft", "confirmed"]
        purchase_count = self.env["im.purchase.order"].search_count(
            [("state", "in", open_states)]
        )
        sale_count = self.env["im.sale.order"].search_count([("state", "in", open_states)])
        return purchase_count + sale_count

    def _get_recent_moves_breakdown(self):
        since = fields.Datetime.now() - timedelta(days=RECENT_MOVES_WINDOW_DAYS)
        moves = self.env["im.move"].search(
            [("state", "=", "done"), ("done_date", ">=", since)]
        )
        receipts = moves.filtered("purchase_line_id")
        deliveries = moves.filtered("shipment_id")
        adjustments = moves.filtered("adjustment_id")
        transfers = moves - receipts - deliveries - adjustments
        return {
            "total": len(moves),
            "receipts": len(receipts),
            "deliveries": len(deliveries),
            "adjustments": len(adjustments),
            "transfers": len(transfers),
        }

    def _get_top_movers(self):
        since = fields.Datetime.now() - timedelta(days=TOP_MOVERS_WINDOW_DAYS)
        groups = self.env["im.move"]._read_group(
            [("state", "=", "done"), ("done_date", ">=", since)],
            groupby=["product_id"],
            aggregates=["quantity:sum"],
            order="quantity:sum desc",
            limit=TOP_MOVERS_LIMIT,
        )
        return [
            {"label": product.name, "value": quantity}
            for product, quantity in groups
            if product
        ]
