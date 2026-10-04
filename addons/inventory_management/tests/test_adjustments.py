from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestAdjustments(TransactionCase):
    def setUp(self):
        super().setUp()
        self.warehouse = self.env["im.warehouse"].create({"name": "Test Warehouse"})
        self.location = self.env["im.location"].create(
            {"name": "Storage", "warehouse_id": self.warehouse.id, "type": "internal"}
        )
        self.category = self.env["im.product.category"].create({"name": "Test Category"})
        self.product = self.env["im.product"].create(
            {"name": "Test Product", "sku": "ADJ-0001", "category_id": self.category.id}
        )

    def test_increase_adjustment_raises_stock(self):
        adjustment = self.env["im.adjustment"].create(
            {
                "product_id": self.product.id,
                "location_id": self.location.id,
                "adjustment_type": "increase",
                "quantity": 5,
                "reason": "Physical count correction",
            }
        )
        adjustment.action_confirm()
        self.assertEqual(adjustment.state, "confirmed")
        self.assertEqual(len(adjustment.move_ids), 1)
        self.assertEqual(adjustment.move_ids.state, "done")
        self.assertEqual(self.product.qty_on_hand, 5)

    def test_decrease_adjustment_below_zero_rejected(self):
        adjustment = self.env["im.adjustment"].create(
            {
                "product_id": self.product.id,
                "location_id": self.location.id,
                "adjustment_type": "decrease",
                "quantity": 5,
                "reason": "Damage write-off",
            }
        )
        with self.assertRaises(ValidationError):
            adjustment.action_confirm()

    def test_decrease_adjustment_within_stock_succeeds(self):
        increase = self.env["im.adjustment"].create(
            {
                "product_id": self.product.id,
                "location_id": self.location.id,
                "adjustment_type": "increase",
                "quantity": 10,
                "reason": "Initial stock",
            }
        )
        increase.action_confirm()

        decrease = self.env["im.adjustment"].create(
            {
                "product_id": self.product.id,
                "location_id": self.location.id,
                "adjustment_type": "decrease",
                "quantity": 3,
                "reason": "Damage write-off",
            }
        )
        decrease.action_confirm()
        self.assertEqual(self.product.qty_on_hand, 7)

    def test_reason_required(self):
        with self.assertRaises(Exception):
            self.env["im.adjustment"].create(
                {
                    "product_id": self.product.id,
                    "location_id": self.location.id,
                    "adjustment_type": "increase",
                    "quantity": 5,
                }
            )

    def test_editing_confirmed_adjustment_rejected(self):
        adjustment = self.env["im.adjustment"].create(
            {
                "product_id": self.product.id,
                "location_id": self.location.id,
                "adjustment_type": "increase",
                "quantity": 5,
                "reason": "Physical count correction",
            }
        )
        adjustment.action_confirm()
        with self.assertRaises(ValidationError):
            adjustment.write({"quantity": 99})
