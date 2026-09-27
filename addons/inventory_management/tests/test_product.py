from odoo.tests.common import TransactionCase
from odoo.tools import mute_logger


class TestProduct(TransactionCase):
    def test_category_and_product_creation(self):
        category = self.env["im.product.category"].create({"name": "Test Category"})
        product = self.env["im.product"].create(
            {
                "name": "Test Product",
                "sku": "TST-0001",
                "category_id": category.id,
            }
        )
        self.assertEqual(product.category_id, category)
        self.assertEqual(product.name, "Test Product")

    def test_duplicate_sku_rejected(self):
        category = self.env["im.product.category"].create({"name": "Test Category"})
        self.env["im.product"].create(
            {"name": "Product A", "sku": "DUP-0001", "category_id": category.id}
        )
        with self.assertRaises(Exception), mute_logger("odoo.sql_db"):
            self.env["im.product"].create(
                {"name": "Product B", "sku": "DUP-0001", "category_id": category.id}
            )

    def test_category_requires_name(self):
        with self.assertRaises(Exception), mute_logger("odoo.sql_db"):
            self.env["im.product.category"].create({})

    def test_product_requires_category(self):
        with self.assertRaises(Exception), mute_logger("odoo.sql_db"):
            self.env["im.product"].create({"name": "No Category Product", "sku": "NOC-0001"})

    def test_product_requires_sku(self):
        category = self.env["im.product.category"].create({"name": "Test Category"})
        with self.assertRaises(Exception), mute_logger("odoo.sql_db"):
            self.env["im.product"].create({"name": "No SKU Product", "category_id": category.id})
