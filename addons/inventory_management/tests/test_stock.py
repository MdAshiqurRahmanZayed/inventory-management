from odoo.exceptions import ValidationError

from .common import BaseTransactionCase


class TestStock(BaseTransactionCase):
    def setUp(self):
        super().setUp()
        self.warehouse = self._create_warehouse()
        self.location_a = self._create_location(self.warehouse, name="Location A")
        self.location_b = self._create_location(self.warehouse, name="Location B")
        self.category = self._create_category()
        self.product = self._create_product(self.category, sku="STK-0001")

    def test_quant_created_and_accumulates(self):
        self._receive(self.product, self.location_a, 10)
        quant = self.env["im.quant"].search(
            [("product_id", "=", self.product.id), ("location_id", "=", self.location_a.id)]
        )
        self.assertEqual(len(quant), 1)
        self.assertEqual(quant.quantity, 10)

        self._receive(self.product, self.location_a, 5)
        quant = self.env["im.quant"].search(
            [("product_id", "=", self.product.id), ("location_id", "=", self.location_a.id)]
        )
        self.assertEqual(len(quant), 1)
        self.assertEqual(quant.quantity, 15)

    def test_negative_stock_rejected(self):
        self._receive(self.product, self.location_a, 5)
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

        self._receive(self.product, self.location_a, 5)
        quant = self.env["im.quant"].search(
            [("product_id", "=", self.product.id), ("location_id", "=", self.location_a.id)]
        )
        with self.assertRaises(ValidationError):
            quant.write({"quantity": 999})

    def test_qty_on_hand_sums_across_locations(self):
        self.assertEqual(self.product.qty_on_hand, 0)
        self._receive(self.product, self.location_a, 10)
        self._receive(self.product, self.location_b, 5)
        self.assertEqual(self.product.qty_on_hand, 15)

    def test_move_requires_a_location(self):
        with self.assertRaises(ValidationError):
            self.env["im.move"].create({"product_id": self.product.id, "quantity": 1})

    def test_move_rejects_more_than_one_origin(self):
        supplier = self._create_partner("Test Supplier", "supplier")
        order = self.env["im.purchase.order"].create(
            {"supplier_id": supplier.id, "warehouse_id": self.warehouse.id}
        )
        line = self.env["im.purchase.line"].create(
            {"order_id": order.id, "product_id": self.product.id, "quantity": 1}
        )
        customer = self._create_partner("Test Customer", "customer")
        sale_order = self.env["im.sale.order"].create(
            {"customer_id": customer.id, "warehouse_id": self.warehouse.id}
        )
        shipment = self.env["im.shipment"].create(
            {"sale_order_id": sale_order.id, "warehouse_id": self.warehouse.id}
        )
        with self.assertRaises(ValidationError):
            self.env["im.move"].create(
                {
                    "product_id": self.product.id,
                    "quantity": 1,
                    "dest_id": self.location_a.id,
                    "purchase_line_id": line.id,
                    "shipment_id": shipment.id,
                }
            )
