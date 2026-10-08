from .common import BaseTransactionCase


class TestAlerts(BaseTransactionCase):
    def setUp(self):
        super().setUp()
        self.category = self._create_category()
        self.responsible = self.env["res.users"].create(
            {"name": "Responsible", "login": "alert.responsible@example.com"}
        )
        self.fallback = self.env["res.users"].create(
            {"name": "Fallback", "login": "alert.fallback@example.com"}
        )

    def _low_stock_product(self, **extra):
        vals = {"reorder_level": 10}
        vals.update(extra)
        return self._create_product(self.category, name="Low Stock Product", sku="ALERT-0001", **vals)

    def test_scan_creates_one_open_alert_and_no_duplicate(self):
        product = self._low_stock_product()
        self.env["im.alert"]._run_low_stock_scan()
        self.env["im.alert"]._run_low_stock_scan()
        alerts = self.env["im.alert"].search([("product_id", "=", product.id)])
        self.assertEqual(len(alerts), 1)
        self.assertEqual(alerts.state, "open")

    def test_activity_assigned_to_responsible_user(self):
        product = self._low_stock_product(responsible_user_id=self.responsible.id)
        self.env["im.alert"]._run_low_stock_scan()
        activities = self.env["mail.activity"].search(
            [("res_model", "=", "im.product"), ("res_id", "=", product.id)]
        )
        self.assertEqual(len(activities), 1)
        self.assertEqual(activities.user_id, self.responsible)

    def test_activity_falls_back_when_no_responsible_user(self):
        self.env["ir.config_parameter"].sudo().set_param(
            "inventory_management.low_stock_fallback_user_id", str(self.fallback.id)
        )
        product = self._low_stock_product()
        self.env["im.alert"]._run_low_stock_scan()
        activities = self.env["mail.activity"].search(
            [("res_model", "=", "im.product"), ("res_id", "=", product.id)]
        )
        self.assertEqual(len(activities), 1)
        self.assertEqual(activities.user_id, self.fallback)

    def test_no_activity_without_responsible_or_fallback(self):
        product = self._low_stock_product()
        self.env["im.alert"]._run_low_stock_scan()
        alerts = self.env["im.alert"].search([("product_id", "=", product.id)])
        self.assertEqual(len(alerts), 1)
        activities = self.env["mail.activity"].search(
            [("res_model", "=", "im.product"), ("res_id", "=", product.id)]
        )
        self.assertFalse(activities)
