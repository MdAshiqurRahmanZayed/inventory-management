from odoo import fields

from .common import BaseTransactionCase


class TestDashboard(BaseTransactionCase):
    def setUp(self):
        super().setUp()
        self.category = self._create_category()
        self.warehouse = self._create_warehouse()
        self.location = self._create_location(
            self.warehouse, is_default_receiving=True, is_default_shipping=True
        )

    def _dashboard_data(self):
        return self.env["im.dashboard"].get_dashboard_data()

    # -- stock value ---------------------------------------------------

    def test_stock_value_is_zero_with_no_quants(self):
        self.assertEqual(self._dashboard_data()["stock_value"], 0)

    def test_stock_value_sums_quantity_times_cost(self):
        product_a = self._create_product(self.category, sku="DASH-A", cost=2.5)
        product_b = self._create_product(self.category, name="Product B", sku="DASH-B", cost=4.0)
        self._receive(product_a, self.location, 10)  # 10 * 2.5 = 25
        self._receive(product_b, self.location, 3)  # 3 * 4.0 = 12
        self.assertEqual(self._dashboard_data()["stock_value"], 25 + 12)

    def test_stock_value_is_a_stored_field_kept_in_sync(self):
        # Regression test for the qty_on_hand/stock_value store=True refactor:
        # both must stay correct through the ORM's dependency tracking alone,
        # with no manual invalidate/recompute call anywhere in the move flow.
        product = self._create_product(self.category, sku="DASH-STORED", cost=2.0)
        self.assertEqual(product.qty_on_hand, 0)
        self.assertEqual(product.stock_value, 0)

        self._receive(product, self.location, 5)
        self.assertEqual(product.qty_on_hand, 5)
        self.assertEqual(product.stock_value, 10)

        # Changing cost alone (no stock movement) must also recompute stock_value.
        product.cost = 3.0
        self.assertEqual(product.stock_value, 15)

    # -- low stock -------------------------------------------------------

    def test_low_stock_count_counts_only_open_alerts(self):
        product_a = self._create_product(self.category, sku="LOW-A", reorder_level=5)
        product_b = self._create_product(self.category, name="Product B", sku="LOW-B", reorder_level=5)
        self.env["im.alert"].create({"product_id": product_a.id, "state": "open"})
        self.env["im.alert"].create({"product_id": product_b.id, "state": "closed"})
        self.assertEqual(self._dashboard_data()["low_stock_count"], 1)

    # -- open orders -------------------------------------------------------

    def test_open_orders_count_excludes_done_and_cancelled(self):
        supplier = self._create_partner("Dash Supplier", "supplier")
        customer = self._create_partner("Dash Customer", "customer")
        product = self._create_product(self.category, sku="OPEN-0001")

        draft_po = self.env["im.purchase.order"].create(
            {"supplier_id": supplier.id, "warehouse_id": self.warehouse.id}
        )
        confirmed_so = self.env["im.sale.order"].create(
            {
                "customer_id": customer.id,
                "warehouse_id": self.warehouse.id,
                "line_ids": [(0, 0, {"product_id": product.id, "quantity": 1})],
            }
        )
        self._receive(product, self.location, 5)
        confirmed_so.action_confirm()

        cancelled_po = self.env["im.purchase.order"].create(
            {"supplier_id": supplier.id, "warehouse_id": self.warehouse.id}
        )
        cancelled_po.action_cancel()

        done_po = self.env["im.purchase.order"].create(
            {
                "supplier_id": supplier.id,
                "warehouse_id": self.warehouse.id,
                "line_ids": [(0, 0, {"product_id": product.id, "quantity": 1})],
            }
        )
        done_po.action_confirm()
        done_po.action_receive_all()
        done_po.action_done()

        self.assertTrue(draft_po)  # kept as a draft, counted
        self.assertEqual(self._dashboard_data()["open_orders_count"], 2)

    # -- recent moves ------------------------------------------------------

    def test_recent_moves_breakdown(self):
        supplier = self._create_partner("Dash Supplier", "supplier")
        customer = self._create_partner("Dash Customer", "customer")
        product = self._create_product(self.category, sku="MOVE-0001")

        # Receipt (purchase_line_id set)
        po = self.env["im.purchase.order"].create(
            {
                "supplier_id": supplier.id,
                "warehouse_id": self.warehouse.id,
                "line_ids": [(0, 0, {"product_id": product.id, "quantity": 20})],
            }
        )
        po.action_confirm()
        po.action_receive_all()

        # Delivery (shipment_id set)
        so = self.env["im.sale.order"].create(
            {
                "customer_id": customer.id,
                "warehouse_id": self.warehouse.id,
                "line_ids": [(0, 0, {"product_id": product.id, "quantity": 5})],
            }
        )
        so.action_confirm()
        so.action_deliver_all()

        # Adjustment (adjustment_id set)
        adjustment = self.env["im.adjustment"].create(
            {
                "product_id": product.id,
                "location_id": self.location.id,
                "adjustment_type": "increase",
                "quantity": 2,
                "reason": "Dashboard test",
            }
        )
        adjustment.action_confirm()

        # Plain transfer (no origin link)
        transfer = self._receive(product, self.location, 1)

        # Outside the 7-day window: should not be counted
        old_transfer = self._receive(product, self.location, 1)
        old_transfer.write(
            {"done_date": fields.Datetime.subtract(fields.Datetime.now(), days=8)}
        )

        breakdown = self._dashboard_data()["recent_moves"]
        self.assertEqual(breakdown["receipts"], 1)
        self.assertEqual(breakdown["deliveries"], 1)
        self.assertEqual(breakdown["adjustments"], 1)
        self.assertEqual(breakdown["transfers"], 1)
        self.assertEqual(breakdown["total"], 4)
        self.assertEqual(
            breakdown["total"],
            breakdown["receipts"] + breakdown["deliveries"]
            + breakdown["adjustments"] + breakdown["transfers"],
        )
        self.assertTrue(transfer)

    def test_recent_moves_excludes_non_done(self):
        product = self._create_product(self.category, sku="MOVE-DRAFT")
        self.env["im.move"].create(
            {"product_id": product.id, "quantity": 5, "dest_id": self.location.id}
        )
        self.assertEqual(self._dashboard_data()["recent_moves"]["total"], 0)

    def test_recent_moves_window_is_configurable(self):
        product = self._create_product(self.category, sku="MOVE-WINDOW")
        move_3_days_ago = self._receive(product, self.location, 1)
        move_3_days_ago.write(
            {"done_date": fields.Datetime.subtract(fields.Datetime.now(), days=3)}
        )
        self._receive(product, self.location, 1)  # today

        # Default (7 days): both count.
        self.assertEqual(self._dashboard_data()["recent_moves"]["total"], 2)

        # Narrow the window to 1 day: only today's move counts.
        self.env["ir.config_parameter"].sudo().set_param(
            "inventory_management.recent_moves_window_days", "1"
        )
        self.assertEqual(self._dashboard_data()["recent_moves"]["total"], 1)

    def test_recent_moves_window_ignores_invalid_param(self):
        self.env["ir.config_parameter"].sudo().set_param(
            "inventory_management.recent_moves_window_days", "not-a-number"
        )
        product = self._create_product(self.category, sku="MOVE-BADPARAM")
        self._receive(product, self.location, 1)
        # Falls back to the 7-day default instead of raising.
        self.assertEqual(self._dashboard_data()["recent_moves"]["total"], 1)

    # -- top movers ----------------------------------------------------

    def test_top_movers_ranking(self):
        product_a = self._create_product(self.category, sku="TOP-A")
        product_b = self._create_product(self.category, name="Product B", sku="TOP-B")
        self._receive(product_a, self.location, 50)
        self._receive(product_b, self.location, 30)

        top_movers = self._dashboard_data()["top_movers"]
        self.assertEqual(len(top_movers), 2)
        self.assertEqual(top_movers[0]["label"], product_a.name)
        self.assertEqual(top_movers[0]["value"], 50)
        self.assertEqual(top_movers[1]["label"], product_b.name)
        self.assertEqual(top_movers[1]["value"], 30)

    def test_top_movers_does_not_pad_with_placeholders(self):
        product = self._create_product(self.category, sku="TOP-ONLY")
        self._receive(product, self.location, 10)
        top_movers = self._dashboard_data()["top_movers"]
        self.assertEqual(len(top_movers), 1)

    def test_top_movers_empty_when_no_recent_activity(self):
        self.assertEqual(self._dashboard_data()["top_movers"], [])

    def test_top_movers_window_is_configurable(self):
        product = self._create_product(self.category, sku="TOP-WINDOW")
        old_move = self._receive(product, self.location, 10)
        old_move.write(
            {"done_date": fields.Datetime.subtract(fields.Datetime.now(), days=10)}
        )

        # Default (30 days): counted.
        self.assertEqual(len(self._dashboard_data()["top_movers"]), 1)

        # Narrow the window to 5 days: no longer counted.
        self.env["ir.config_parameter"].sudo().set_param(
            "inventory_management.top_movers_window_days", "5"
        )
        self.assertEqual(self._dashboard_data()["top_movers"], [])
