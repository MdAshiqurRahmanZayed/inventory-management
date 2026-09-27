from odoo import api
from odoo import models


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
        }
