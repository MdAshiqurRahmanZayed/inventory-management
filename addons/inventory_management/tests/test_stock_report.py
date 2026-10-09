from .common import BaseTransactionCase


class TestStockReport(BaseTransactionCase):
    def setUp(self):
        super().setUp()
        self.category = self._create_category()
        self.warehouse_a = self._create_warehouse(name="Warehouse A")
        self.warehouse_b = self._create_warehouse(name="Warehouse B")
        self.location_a = self._create_location(self.warehouse_a, is_default_receiving=True)
        self.location_b = self._create_location(self.warehouse_b, is_default_receiving=True)

    def test_report_lines_scoped_to_one_warehouse(self):
        product_a = self._create_product(self.category, sku="RPT-A", cost=3.0)
        product_b = self._create_product(self.category, name="Product B", sku="RPT-B", cost=5.0)
        self._receive(product_a, self.location_a, 10)
        self._receive(product_b, self.location_b, 4)

        lines, total = self.warehouse_a.get_stock_report_lines()
        self.assertEqual(len(lines), 1)
        self.assertEqual(lines[0]["product"], product_a)
        self.assertEqual(lines[0]["quantity"], 10)
        self.assertEqual(lines[0]["value"], 30)
        self.assertEqual(total, 30)

    def test_zero_stock_product_excluded(self):
        product = self._create_product(self.category, sku="RPT-ZERO", cost=2.0)
        self.env["im.quant"].sudo().with_context(im_allow_quant_write=True).create(
            {"product_id": product.id, "location_id": self.location_a.id, "quantity": 0}
        )
        lines, total = self.warehouse_a.get_stock_report_lines()
        self.assertEqual(lines, [])
        self.assertEqual(total, 0)

    def test_report_aggregates_across_warehouse_locations(self):
        product = self._create_product(self.category, sku="RPT-MULTI", cost=1.5)
        second_location = self._create_location(self.warehouse_a, name="Second Location")
        self._receive(product, self.location_a, 6)
        self._receive(product, second_location, 4)

        lines, total = self.warehouse_a.get_stock_report_lines()
        self.assertEqual(len(lines), 1)
        self.assertEqual(lines[0]["quantity"], 10)
        self.assertEqual(total, 15)

    def test_report_action_is_bound_to_warehouse(self):
        action = self.env.ref("inventory_management.action_report_im_stock_report")
        self.assertEqual(action.model, "im.warehouse")
        self.assertEqual(action.report_type, "qweb-pdf")
        self.assertEqual(action.binding_model_id.model, "im.warehouse")
