from odoo.exceptions import AccessError

from .common import BaseTransactionCase


class TestAccessControl(BaseTransactionCase):
    def setUp(self):
        super().setUp()
        self.warehouse = self._create_warehouse(name="Access Test Warehouse")
        self.location = self._create_location(
            self.warehouse, name="Access Test Location", is_default_receiving=True
        )
        self.category = self._create_category(name="Access Test Category")
        self.product = self._create_product(self.category, name="Access Test Product", sku="ACC-0001")
        self.supplier = self._create_partner("Access Test Supplier", "supplier")
        self.viewer = self._create_role_user("Access Viewer", "access.viewer@example.com", "viewer")
        self.user_a = self._create_role_user("Access User A", "access.user.a@example.com", "user")
        self.user_b = self._create_role_user("Access User B", "access.user.b@example.com", "user")
        self.manager = self._create_role_user("Access Manager", "access.manager@example.com", "manager")

    def test_viewer_cannot_write_product(self):
        with self.assertRaises(AccessError):
            self.product.with_user(self.viewer).write({"reorder_level": 5})

    def test_user_cannot_confirm_purchase_order(self):
        order = self.env["im.purchase.order"].with_user(self.user_a).create(
            {
                "supplier_id": self.supplier.id,
                "warehouse_id": self.warehouse.id,
                "line_ids": [(0, 0, {"product_id": self.product.id, "quantity": 1})],
            }
        )
        with self.assertRaises(AccessError):
            order.with_user(self.user_a).action_confirm()

    def test_manager_can_confirm_purchase_order(self):
        order = self.env["im.purchase.order"].with_user(self.manager).create(
            {
                "supplier_id": self.supplier.id,
                "warehouse_id": self.warehouse.id,
                "line_ids": [(0, 0, {"product_id": self.product.id, "quantity": 1})],
            }
        )
        order.with_user(self.manager).action_confirm()
        self.assertEqual(order.state, "confirmed")

    def test_user_edits_only_their_own_move(self):
        move = self.env["im.move"].with_user(self.user_a).create(
            {"product_id": self.product.id, "quantity": 1, "dest_id": self.location.id}
        )
        move.with_user(self.user_a).write({"quantity": 2})
        self.assertEqual(move.quantity, 2)
        with self.assertRaises(AccessError):
            move.with_user(self.user_b).write({"quantity": 3})

    def test_user_can_confirm_and_receive_their_own_move(self):
        move = self.env["im.move"].with_user(self.user_a).create(
            {"product_id": self.product.id, "quantity": 1, "dest_id": self.location.id}
        )
        move.with_user(self.user_a).write({"state": "confirmed"})
        move.with_user(self.user_a).write({"state": "done"})
        self.assertEqual(move.state, "done")

    def test_done_move_is_read_only_for_everyone_including_manager(self):
        move = self.env["im.move"].with_user(self.user_a).create(
            {"product_id": self.product.id, "quantity": 1, "dest_id": self.location.id}
        )
        move.write({"state": "confirmed"})
        move.write({"state": "done"})
        with self.assertRaises(AccessError):
            move.with_user(self.manager).unlink()

    def test_role_management_app_is_manager_only(self):
        role_manager_group = self.env.ref("role_management.group_role_manager")
        self.assertIn(role_manager_group, self.manager.all_group_ids)
        self.assertNotIn(role_manager_group, self.user_a.all_group_ids)
        self.assertNotIn(role_manager_group, self.viewer.all_group_ids)
