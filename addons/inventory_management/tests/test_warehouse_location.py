from odoo.tools import mute_logger

from .common import BaseTransactionCase


class TestWarehouseLocation(BaseTransactionCase):
    def test_warehouse_and_location_creation(self):
        warehouse = self._create_warehouse(address="1 Test Street")
        location = self._create_location(warehouse)
        self.assertEqual(location.warehouse_id, warehouse)
        self.assertIn(location, warehouse.location_ids)

    def test_location_requires_warehouse(self):
        with self.assertRaises(Exception), mute_logger("odoo.sql_db"):
            self.env["im.location"].create({"name": "Orphan Location", "type": "internal"})

    def test_warehouse_requires_name(self):
        with self.assertRaises(Exception), mute_logger("odoo.sql_db"):
            self.env["im.warehouse"].create({"address": "No Name Street"})

    def test_location_defaults_to_internal_type(self):
        warehouse = self._create_warehouse(name="Default Type Warehouse")
        location = self.env["im.location"].create(
            {"name": "Default Type Location", "warehouse_id": warehouse.id}
        )
        self.assertEqual(location.type, "internal")
