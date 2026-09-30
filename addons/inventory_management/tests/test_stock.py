from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestStock(TransactionCase):
    def setUp(self):
        super().setUp()
        self.warehouse = self.env["im.warehouse"].create({"name": "Test Warehouse"})
        self.location_a = self.env["im.location"].create(
            {"name": "Location A", "warehouse_id": self.warehouse.id, "type": "internal"}
        )
        self.location_b = self.env["im.location"].create(
            {"name": "Location B", "warehouse_id": self.warehouse.id, "type": "internal"}
        )
        self.category = self.env["im.product.category"].create({"name": "Test Category"})
        self.product = self.env["im.product"].create(
            {"name": "Test Product", "sku": "STK-0001", "category_id": self.category.id}
        )

    def _receive(self, location, quantity):
        move = self.env["im.move"].create(
            {"product_id": self.product.id, "quantity": quantity, "dest_id": location.id}
        )
        move.write({"state": "confirmed"})
        move.write({"state": "done"})
        return move

    def test_quant_created_and_accumulates(self):
        self._receive(self.location_a, 10)
        quant = self.env["im.quant"].search(
            [("product_id", "=", self.product.id), ("location_id", "=", self.location_a.id)]
        )
        self.assertEqual(len(quant), 1)
        self.assertEqual(quant.quantity, 10)

        self._receive(self.location_a, 5)
        quant = self.env["im.quant"].search(
            [("product_id", "=", self.product.id), ("location_id", "=", self.location_a.id)]
        )
        self.assertEqual(len(quant), 1)
        self.assertEqual(quant.quantity, 15)

    def test_negative_stock_rejected(self):
        self._receive(self.location_a, 5)
        move = self.env["im.move"].create(
            {
                "product_id": self.product.id,
                "quantity": 10,
                "source_id": self.location_a.id,
                "dest_id": self.location_b.id,
            }
        )
        move.write({"state": "confirmed"})
        with self.assertRaises(ValidationError):
            move.write({"state": "done"})

    def test_direct_quant_write_rejected(self):
        with self.assertRaises(ValidationError):
            self.env["im.quant"].create(
                {"product_id": self.product.id, "location_id": self.location_a.id, "quantity": 5}
            )

        self._receive(self.location_a, 5)
        quant = self.env["im.quant"].search(
            [("product_id", "=", self.product.id), ("location_id", "=", self.location_a.id)]
        )
        with self.assertRaises(ValidationError):
            quant.write({"quantity": 999})

    def test_qty_on_hand_sums_across_locations(self):
        self.assertEqual(self.product.qty_on_hand, 0)
        self._receive(self.location_a, 10)
        self._receive(self.location_b, 5)
        self.assertEqual(self.product.qty_on_hand, 15)

    def test_move_requires_a_location(self):
        with self.assertRaises(ValidationError):
            self.env["im.move"].create({"product_id": self.product.id, "quantity": 1})
