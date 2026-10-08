from .common import BaseTransactionCase


class TestPartnerRoles(BaseTransactionCase):
    def test_both_role_computes_both_flags(self):
        partner = self._create_partner("Both Co", "both")
        self.assertTrue(partner.is_supplier)
        self.assertTrue(partner.is_customer)

    def test_single_role_computes_single_flag(self):
        supplier = self._create_partner("Supplier Co", "supplier")
        self.assertTrue(supplier.is_supplier)
        self.assertFalse(supplier.is_customer)

        customer = self._create_partner("Customer Co", "customer")
        self.assertFalse(customer.is_supplier)
        self.assertTrue(customer.is_customer)

    def test_search_filter_by_role(self):
        supplier = self._create_partner("Filter Supplier Co", "supplier")
        customer = self._create_partner("Filter Customer Co", "customer")
        suppliers = self.env["res.partner"].search([("is_supplier", "=", True)])
        self.assertIn(supplier, suppliers)
        self.assertNotIn(customer, suppliers)
