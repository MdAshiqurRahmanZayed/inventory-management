from odoo.tests.common import TransactionCase
from odoo.tools import mute_logger


class TestWarehouseLocation(TransactionCase):
    def test_warehouse_and_location_creation(self):
        warehouse = self.env["im.warehouse"].create(
            {"name": "Test Warehouse", "address": "1 Test Street"}
        )
        location = self.env["im.location"].create(
            {"name": "Test Location", "warehouse_id": warehouse.id, "type": "internal"}
        )
        self.assertEqual(location.warehouse_id, warehouse)
        self.assertIn(location, warehouse.location_ids)

    def test_location_requires_warehouse(self):
        with self.assertRaises(Exception), mute_logger("odoo.sql_db"):
            self.env["im.location"].create({"name": "Orphan Location", "type": "internal"})

    def test_warehouse_requires_name(self):
        with self.assertRaises(Exception), mute_logger("odoo.sql_db"):
            self.env["im.warehouse"].create({"address": "No Name Street"})

    def test_location_defaults_to_internal_type(self):
        warehouse = self.env["im.warehouse"].create({"name": "Default Type Warehouse"})
        location = self.env["im.location"].create(
            {"name": "Default Type Location", "warehouse_id": warehouse.id}
        )
        self.assertEqual(location.type, "internal")
