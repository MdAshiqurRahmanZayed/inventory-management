from odoo.tools import mute_logger

from .common import BaseTransactionCase


class TestProduct(BaseTransactionCase):
    def test_category_and_product_creation(self):
        category = self._create_category()
        product = self._create_product(category, name="Test Product", sku="TST-0001")
        self.assertEqual(product.category_id, category)
        self.assertEqual(product.name, "Test Product")

    def test_duplicate_sku_rejected(self):
        category = self._create_category()
        self._create_product(category, name="Product A", sku="DUP-0001")
        with self.assertRaises(Exception), mute_logger("odoo.sql_db"):
            self._create_product(category, name="Product B", sku="DUP-0001")

    def test_category_requires_name(self):
        with self.assertRaises(Exception), mute_logger("odoo.sql_db"):
            self.env["im.product.category"].create({})

    def test_product_requires_category(self):
        with self.assertRaises(Exception), mute_logger("odoo.sql_db"):
            self.env["im.product"].create({"name": "No Category Product", "sku": "NOC-0001"})

    def test_product_requires_sku(self):
        category = self._create_category()
        with self.assertRaises(Exception), mute_logger("odoo.sql_db"):
            self.env["im.product"].create({"name": "No SKU Product", "category_id": category.id})
