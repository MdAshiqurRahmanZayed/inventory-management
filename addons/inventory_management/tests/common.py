from odoo.tests.common import TransactionCase


class BaseTransactionCase(TransactionCase):
    """Base TransactionCase for inventory_management tests.

    Centralizes the fixture boilerplate (category/product/warehouse/location/
    partner/role-user creation) that individual test modules otherwise each
    reimplement, so test setUp methods stay short and the fixtures stay
    consistent across modules.
    """

    def _create_category(self, name="Test Category"):
        return self.env["im.product.category"].create({"name": name})

    def _create_product(self, category, name="Test Product", sku="TST-0001", **extra):
        vals = {"name": name, "sku": sku, "category_id": category.id}
        vals.update(extra)
        return self.env["im.product"].create(vals)

    def _create_warehouse(self, name="Test Warehouse", **extra):
        vals = {"name": name}
        vals.update(extra)
        return self.env["im.warehouse"].create(vals)

    def _create_location(self, warehouse, name="Test Location", location_type="internal", **extra):
        vals = {"name": name, "warehouse_id": warehouse.id, "type": location_type}
        vals.update(extra)
        return self.env["im.location"].create(vals)

    def _create_partner(self, name, partner_role):
        return self.env["res.partner"].create({"name": name, "partner_role": partner_role})

    def _create_role_user(self, name, login, role):
        """role is one of 'viewer', 'user', 'manager'."""
        group = self.env.ref(f"inventory_management.group_stock_{role}")
        internal = self.env.ref("base.group_user")
        return self.env["res.users"].create(
            {"name": name, "login": login, "group_ids": [(6, 0, [internal.id, group.id])]}
        )

    def _receive(self, product, location, quantity):
        """Create a Done receipt move for product/quantity into location."""
        move = self.env["im.move"].create(
            {"product_id": product.id, "quantity": quantity, "dest_id": location.id}
        )
        move.write({"state": "confirmed"})
        move.write({"state": "done"})
        return move
