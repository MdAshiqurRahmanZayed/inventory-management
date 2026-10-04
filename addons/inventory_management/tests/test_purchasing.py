from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestPurchasing(TransactionCase):
    def setUp(self):
        super().setUp()
        self.supplier = self.env["res.partner"].create(
            {"name": "Test Supplier", "partner_role": "supplier"}
        )
        self.warehouse = self.env["im.warehouse"].create({"name": "Test Warehouse"})
        self.receiving = self.env["im.location"].create(
            {
                "name": "Receiving",
                "warehouse_id": self.warehouse.id,
                "type": "internal",
                "is_default_receiving": True,
            }
        )
        self.category = self.env["im.product.category"].create({"name": "Test Category"})
        self.product_a = self.env["im.product"].create(
            {"name": "Product A", "sku": "PA-0001", "category_id": self.category.id}
        )
        self.product_b = self.env["im.product"].create(
            {"name": "Product B", "sku": "PB-0001", "category_id": self.category.id}
        )

    def _create_order(self, lines):
        return self.env["im.purchase.order"].create(
            {
                "supplier_id": self.supplier.id,
                "warehouse_id": self.warehouse.id,
                "line_ids": [(0, 0, line) for line in lines],
            }
        )

    def test_confirm_creates_correct_moves(self):
        order = self._create_order(
            [
                {"product_id": self.product_a.id, "quantity": 10, "unit_cost": 5.0},
                {"product_id": self.product_b.id, "quantity": 4, "unit_cost": 2.0},
            ]
        )
        order.action_confirm()
        self.assertEqual(order.state, "confirmed")
        self.assertEqual(len(order.move_ids), 2)
        for move, line in zip(order.move_ids.sorted("id"), order.line_ids.sorted("id")):
            self.assertEqual(move.product_id, line.product_id)
            self.assertEqual(move.quantity, line.quantity)
            self.assertEqual(move.dest_id, self.receiving)
            self.assertFalse(move.source_id)
            self.assertEqual(move.purchase_line_id, line)
            self.assertEqual(move.state, "draft")

    def test_confirm_requires_at_least_one_line(self):
        order = self._create_order([])
        with self.assertRaises(ValidationError):
            order.action_confirm()

    def test_move_state_skip_rejected(self):
        order = self._create_order([{"product_id": self.product_a.id, "quantity": 5}])
        order.action_confirm()
        move = order.move_ids
        with self.assertRaises(ValidationError):
            move.write({"state": "done"})

    def test_done_move_is_immutable(self):
        order = self._create_order([{"product_id": self.product_a.id, "quantity": 5}])
        order.action_confirm()
        move = order.move_ids
        move.write({"state": "confirmed"})
        move.write({"state": "done"})
        with self.assertRaises(ValidationError):
            move.write({"quantity": 99})

    def test_receive_all_marks_moves_done(self):
        order = self._create_order(
            [
                {"product_id": self.product_a.id, "quantity": 5},
                {"product_id": self.product_b.id, "quantity": 3},
            ]
        )
        order.action_confirm()
        order.action_receive_all()
        self.assertTrue(all(move.state == "done" for move in order.move_ids))
        order.action_done()
        self.assertEqual(order.state, "done")

    def test_order_done_guard(self):
        order = self._create_order(
            [
                {"product_id": self.product_a.id, "quantity": 5},
                {"product_id": self.product_b.id, "quantity": 3},
            ]
        )
        order.action_confirm()
        moves = order.move_ids.sorted("id")
        moves[0].write({"state": "confirmed"})
        moves[0].write({"state": "done"})
        with self.assertRaises(ValidationError):
            order.action_done()
        moves[1].write({"state": "confirmed"})
        moves[1].write({"state": "done"})
        order.action_done()
        self.assertEqual(order.state, "done")
