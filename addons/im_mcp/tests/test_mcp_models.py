from odoo.addons.inventory_management.tests.common import BaseTransactionCase
from odoo.exceptions import AccessError
from odoo.exceptions import ValidationError


class TestMcpConnectorAccess(BaseTransactionCase):
    def setUp(self):
        super().setUp()
        self.manager = self._create_role_user("Mgr", "mcp_mgr@test.com", "manager")
        self.user = self._create_role_user("Usr", "mcp_user@test.com", "user")
        self.connector = self.env["im.mcp.connector"].create(
            {"name": "Test Connector", "user_id": self.user.id}
        )

    def test_manager_can_create_and_read(self):
        connector = self.env["im.mcp.connector"].with_user(self.manager).create(
            {"name": "Another", "user_id": self.user.id}
        )
        self.assertTrue(connector.exists())

    def test_user_cannot_access_connector(self):
        with self.assertRaises(AccessError):
            self.env["im.mcp.connector"].with_user(self.user).search([])


class TestMcpAccessRule(BaseTransactionCase):
    def setUp(self):
        super().setUp()
        self.product_model = self.env["ir.model"].search([("model", "=", "im.product")], limit=1)

    def test_blocked_models_rejected(self):
        for model_name in ("res.users", "ir.model", "im.mcp.connector", "im.api.log"):
            ir_model = self.env["ir.model"].search([("model", "=", model_name)], limit=1)
            with self.assertRaises(ValidationError):
                self.env["im.mcp.access"].create({"model_id": ir_model.id})

    def test_duplicate_model_rejected(self):
        self.env["im.mcp.access"].create({"model_id": self.product_model.id})
        with self.assertRaises(Exception):
            self.env["im.mcp.access"].create({"model_id": self.product_model.id})

    def test_get_access_granted_ungranted_and_disabled_operation(self):
        access = self.env["im.mcp.access"].create(
            {"model_id": self.product_model.id, "can_read": True, "can_write": False}
        )
        Access = self.env["im.mcp.access"]
        self.assertEqual(Access.get_access("im.product", "read"), access)
        self.assertIsNone(Access.get_access("im.product", "write"))
        self.assertIsNone(Access.get_access("im.warehouse", "read"))

    def test_field_from_another_model_rejected(self):
        warehouse_model = self.env["ir.model"].search([("model", "=", "im.warehouse")], limit=1)
        foreign_field = self.env["ir.model.fields"].search(
            [("model_id", "=", warehouse_model.id), ("name", "=", "name")], limit=1
        )
        with self.assertRaises(ValidationError):
            self.env["im.mcp.access"].create(
                {"model_id": self.product_model.id, "field_ids": [(6, 0, [foreign_field.id])]}
            )

    def test_field_from_same_model_allowed(self):
        own_field = self.env["ir.model.fields"].search(
            [("model_id", "=", self.product_model.id), ("name", "=", "name")], limit=1
        )
        access = self.env["im.mcp.access"].create(
            {"model_id": self.product_model.id, "field_ids": [(6, 0, [own_field.id])]}
        )
        self.assertEqual(access.field_ids, own_field)

    def test_disabled_rule_is_unreachable(self):
        self.env["im.mcp.access"].create(
            {"model_id": self.product_model.id, "enabled": False, "can_read": True}
        )
        self.assertIsNone(self.env["im.mcp.access"].get_access("im.product", "read"))


class TestMcpApiLog(BaseTransactionCase):
    def setUp(self):
        super().setUp()
        self.manager = self._create_role_user("Mgr2", "mcp_mgr2@test.com", "manager")
        self.user_a = self._create_role_user("UsrA", "mcp_a@test.com", "user")
        self.user_b = self._create_role_user("UsrB", "mcp_b@test.com", "user")
        connector = self.env["im.mcp.connector"].create(
            {"name": "C", "user_id": self.user_a.id}
        )
        self.log_a = self.env["im.api.log"].create(
            {"connector_id": connector.id, "user_id": self.user_a.id, "tool": "search_records"}
        )
        self.log_b = self.env["im.api.log"].sudo().create(
            {"connector_id": connector.id, "user_id": self.user_b.id, "tool": "search_records"}
        )

    def test_user_sees_only_own_logs(self):
        logs = self.env["im.api.log"].with_user(self.user_a).search([])
        self.assertIn(self.log_a, logs)
        self.assertNotIn(self.log_b, logs)

    def test_manager_sees_all_logs(self):
        logs = self.env["im.api.log"].with_user(self.manager).search([])
        self.assertIn(self.log_a, logs)
        self.assertIn(self.log_b, logs)


class TestMcpConnectorMenu(BaseTransactionCase):
    def test_menu_restricted_to_manager(self):
        menu = self.env.ref("im_mcp.menu_im_mcp_root")
        manager_group = self.env.ref("inventory_management.group_stock_manager")
        user_group = self.env.ref("inventory_management.group_stock_user")
        self.assertIn(manager_group, menu.group_ids)
        self.assertNotIn(user_group, menu.group_ids)
