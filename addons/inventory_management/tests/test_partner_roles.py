from odoo.tests.common import TransactionCase


class TestPartnerRoles(TransactionCase):
    def test_both_role_computes_both_flags(self):
        partner = self.env["res.partner"].create(
            {"name": "Both Co", "partner_role": "both"}
        )
        self.assertTrue(partner.is_supplier)
        self.assertTrue(partner.is_customer)

    def test_single_role_computes_single_flag(self):
        supplier = self.env["res.partner"].create(
            {"name": "Supplier Co", "partner_role": "supplier"}
        )
        self.assertTrue(supplier.is_supplier)
        self.assertFalse(supplier.is_customer)

        customer = self.env["res.partner"].create(
            {"name": "Customer Co", "partner_role": "customer"}
        )
        self.assertFalse(customer.is_supplier)
        self.assertTrue(customer.is_customer)

    def test_search_filter_by_role(self):
        supplier = self.env["res.partner"].create(
            {"name": "Filter Supplier Co", "partner_role": "supplier"}
        )
        customer = self.env["res.partner"].create(
            {"name": "Filter Customer Co", "partner_role": "customer"}
        )
        suppliers = self.env["res.partner"].search([("is_supplier", "=", True)])
        self.assertIn(supplier, suppliers)
        self.assertNotIn(customer, suppliers)
