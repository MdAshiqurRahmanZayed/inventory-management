from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestSales(TransactionCase):
    def setUp(self):
        super().setUp()
        self.customer = self.env["res.partner"].create(
            {"name": "Test Customer", "partner_role": "customer"}
        )
        self.warehouse = self.env["im.warehouse"].create({"name": "Test Warehouse"})
        self.shipping = self.env["im.location"].create(
            {
                "name": "Shipping",
                "warehouse_id": self.warehouse.id,
                "type": "internal",
                "is_default_shipping": True,
            }
        )
        self.category = self.env["im.product.category"].create({"name": "Test Category"})
        self.product_a = self.env["im.product"].create(
            {"name": "Product A", "sku": "SA-0001", "category_id": self.category.id}
        )
        self.product_b = self.env["im.product"].create(
            {"name": "Product B", "sku": "SB-0001", "category_id": self.category.id}
        )
        self._receive(self.product_a, 20)
        self._receive(self.product_b, 10)

    def _receive(self, product, quantity):
        move = self.env["im.move"].create(
            {"product_id": product.id, "quantity": quantity, "dest_id": self.shipping.id}
        )
        move.write({"state": "confirmed"})
        move.write({"state": "done"})

    def _create_order(self, lines):
        return self.env["im.sale.order"].create(
            {
                "customer_id": self.customer.id,
                "warehouse_id": self.warehouse.id,
                "line_ids": [(0, 0, line) for line in lines],
            }
        )

    def test_confirm_creates_shipment_and_moves(self):
        order = self._create_order(
            [
                {"product_id": self.product_a.id, "quantity": 5, "unit_price": 10.0},
                {"product_id": self.product_b.id, "quantity": 2, "unit_price": 20.0},
            ]
        )
        order.action_confirm()
        self.assertEqual(order.state, "confirmed")
        self.assertTrue(order.shipment_id)
        self.assertEqual(order.shipment_id.status, "confirmed")
        moves = order.shipment_id.move_ids
        self.assertEqual(len(moves), 2)
        for move, line in zip(moves.sorted("id"), order.line_ids.sorted("id")):
            self.assertEqual(move.product_id, line.product_id)
            self.assertEqual(move.quantity, line.quantity)
            self.assertEqual(move.source_id, self.shipping)
            self.assertFalse(move.dest_id)
            self.assertEqual(move.shipment_id, order.shipment_id)
            self.assertEqual(move.state, "draft")

    def test_confirm_requires_at_least_one_line(self):
        order = self._create_order([])
        with self.assertRaises(ValidationError):
            order.action_confirm()

    def test_done_guard_blocked_until_all_moves_done(self):
        order = self._create_order(
            [
                {"product_id": self.product_a.id, "quantity": 5},
                {"product_id": self.product_b.id, "quantity": 2},
            ]
        )
        order.action_confirm()
        moves = order.shipment_id.move_ids.sorted("id")
        moves[0].write({"state": "confirmed"})
        moves[0].write({"state": "done"})
        with self.assertRaises(ValidationError):
            order.action_done()
        moves[1].write({"state": "confirmed"})
        moves[1].write({"state": "done"})
        order.action_done()
        self.assertEqual(order.state, "done")
        self.assertEqual(order.shipment_id.status, "done")

    def test_deliver_all_marks_moves_done_and_decrements_stock(self):
        order = self._create_order([{"product_id": self.product_a.id, "quantity": 5}])
        order.action_confirm()
        order.action_deliver_all()
        self.assertTrue(all(move.state == "done" for move in order.shipment_id.move_ids))
        self.assertEqual(self.product_a.qty_on_hand, 15)

    def test_delivering_below_available_stock_rejected(self):
        order = self._create_order([{"product_id": self.product_a.id, "quantity": 999}])
        order.action_confirm()
        with self.assertRaises(ValidationError):
            order.action_deliver_all()
