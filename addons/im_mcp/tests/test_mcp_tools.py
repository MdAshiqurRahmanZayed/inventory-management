import json

from odoo.addons.im_mcp.services import protocol
from odoo.addons.im_mcp.services import tools
from odoo.addons.inventory_management.tests.common import BaseTransactionCase
from odoo.exceptions import AccessError
from odoo.exceptions import UserError


class McpToolsBase(BaseTransactionCase):
    def setUp(self):
        super().setUp()
        self.category = self._create_category()
        self.product = self._create_product(self.category, name="Widget", sku="WDG-1")
        self.warehouse = self._create_warehouse()
        self.location = self._create_location(self.warehouse)
        self._user_seq = 0

    def _user_env(self, role):
        """A fresh env acting as a new user with the given stock role."""
        self._user_seq += 1
        login = f"mcp_{role}_{self._user_seq}@test.com"
        user = self._create_role_user(f"Mcp {role} {self._user_seq}", login, role)
        return self.env(user=user)

    def _grant(self, model, **ops):
        """Create a fresh access rule for *model*, replacing any that already exists.

        Access rules are global (unique per model), so running this suite against
        a database that already has real rules (e.g. a manually configured dev db)
        must not collide with them. The transaction rolls back after each test, so
        this never touches the real row beyond the test.
        """
        model_id = self.env["ir.model"].search([("model", "=", model)], limit=1).id
        self.env["im.mcp.access"].search([("model_id", "=", model_id)]).unlink()
        return self.env["im.mcp.access"].create({"model_id": model_id, **ops})

    def _revoke(self, model):
        """Ensure no access rule exists for *model*, regardless of what the db already has."""
        self.env["im.mcp.access"].search([("model_name", "=", model)]).unlink()


class TestSearchAndGet(McpToolsBase):
    def setUp(self):
        super().setUp()
        self.c_env = self._user_env("user")
        self._grant("im.product", can_read=True)

    def test_search_allowed_model(self):
        result = tools.search_records(self.c_env, "im.product", domain=[("id", "=", self.product.id)])
        self.assertTrue(any(r["id"] == self.product.id for r in result["records"]))

    def test_search_model_without_access_row(self):
        self._revoke("im.warehouse")
        with self.assertRaises(AccessError):
            tools.search_records(self.c_env, "im.warehouse")

    def test_max_records_caps_results(self):
        self._create_product(self.category, name="Widget 2", sku="WDG-2")
        access = self.env["im.mcp.access"].search([("model_name", "=", "im.product")])
        access.max_records = 1
        result = tools.search_records(self.c_env, "im.product", limit=10)
        self.assertEqual(len(result["records"]), 1)

    def test_get_record(self):
        result = tools.get_record(self.c_env, "im.product", self.product.id)
        self.assertEqual(result["record"]["id"], self.product.id)

    def test_string_limit_and_offset_are_coerced(self):
        """MCP clients sometimes send numbers as strings; must not crash."""
        result = tools.search_records(self.c_env, "im.product", limit="500", offset="0")
        self.assertTrue(any(r["id"] == self.product.id for r in result["records"]))

    def test_string_record_id_is_coerced(self):
        result = tools.get_record(self.c_env, "im.product", str(self.product.id))
        self.assertEqual(result["record"]["id"], self.product.id)

    def test_fields_param_restricts_output(self):
        result = tools.search_records(
            self.c_env, "im.product", domain=[("id", "=", self.product.id)], fields=["name", "sku"]
        )
        record = result["records"][0]
        self.assertEqual(set(record) - {"id"}, {"name", "sku"})

    def test_fields_param_as_json_string(self):
        result = tools.get_record(self.c_env, "im.product", self.product.id, fields='["name"]')
        self.assertEqual(set(result["record"]) - {"id"}, {"name"})

    def test_max_records_zero_blocks_all_results(self):
        access = self.env["im.mcp.access"].search([("model_name", "=", "im.product")])
        access.max_records = 0
        result = tools.search_records(self.c_env, "im.product", limit=10)
        self.assertEqual(result["records"], [])

    def test_disabled_rule_blocks_access(self):
        access = self.env["im.mcp.access"].search([("model_name", "=", "im.product")])
        access.enabled = False
        with self.assertRaises(AccessError):
            tools.search_records(self.c_env, "im.product")


class TestCreateUpdateDelete(McpToolsBase):
    def test_create_allowed(self):
        c_env = self._user_env("manager")
        self._grant("im.product.category", can_create=True)
        result = tools.create_record(c_env, "im.product.category", {"name": "New Category"})
        self.assertTrue(result["id"])

    def test_create_refused_without_grant(self):
        c_env = self._user_env("manager")
        self._grant("im.product.category", can_read=True)
        with self.assertRaises(AccessError):
            tools.create_record(c_env, "im.product.category", {"name": "X"})

    def test_values_as_json_string_is_parsed(self):
        """MCP clients sometimes send the values object as a JSON-encoded string."""
        c_env = self._user_env("manager")
        self._grant("im.product.category", can_create=True)
        result = tools.create_record(c_env, "im.product.category", '{"name": "From JSON string"}')
        category = self.env["im.product.category"].browse(result["id"])
        self.assertEqual(category.name, "From JSON string")

    def test_cannot_exceed_own_user_permission(self):
        # Viewer's native Odoo rights have no write on im.product, even though
        # the global MCP access rule grants it.
        c_env = self._user_env("viewer")
        self._grant("im.product", can_read=True, can_write=True)
        with self.assertRaises(AccessError):
            tools.update_record(c_env, "im.product", self.product.id, {"name": "Hacked"})

    def test_delete_allowed(self):
        c_env = self._user_env("manager")
        self._grant("im.product.category", can_delete=True)
        category = self._create_category(name="Disposable")
        tools.delete_record(c_env, "im.product.category", category.id)
        self.assertFalse(category.exists())


class TestListModels(McpToolsBase):
    # list_models is deliberately global -- it reflects every enabled model,
    # not just what a given test granted -- so assertions check containment,
    # not an exact list, since other rules may already exist in the target db.

    def test_list_models_reflects_global_rules(self):
        self._grant("im.product", can_read=True)
        self._grant("im.warehouse", can_read=True, can_write=True)

        models_by_name = {m["model"]: m for m in tools.list_models(self._user_env("user"))["models"]}

        self.assertEqual(models_by_name["im.product"]["operations"]["read"], True)
        self.assertEqual(models_by_name["im.warehouse"]["operations"]["write"], True)

    def test_list_models_excludes_disabled(self):
        self._grant("im.product", can_read=True)
        access = self._grant("im.warehouse", can_read=True, enabled=False)

        models = [m["model"] for m in tools.list_models(self._user_env("user"))["models"]]

        self.assertIn("im.product", models)
        self.assertNotIn("im.warehouse", models)
        self.assertFalse(access.enabled)


class TestDraftStockMove(McpToolsBase):
    def setUp(self):
        super().setUp()
        self.c_env = self._user_env("manager")
        self._grant("im.move", can_create=True)
        self._grant("im.product", can_read=True)
        self._grant("im.location", can_read=True)

    def test_invalid_product_creates_nothing(self):
        before = self.env["im.move"].search_count([])
        with self.assertRaises(UserError):
            tools.draft_stock_move(self.c_env, product_id=999999, quantity=1, dest_id=self.location.id)
        self.assertEqual(self.env["im.move"].search_count([]), before)

    def test_string_arguments_are_coerced(self):
        """MCP clients sometimes send numbers as strings; must not crash."""
        result = tools.draft_stock_move(
            self.c_env,
            product_id=str(self.product.id),
            quantity="5",
            dest_id=str(self.location.id),
        )
        move = self.env["im.move"].browse(result["id"])
        self.assertEqual(move.quantity, 5)

    def test_missing_product_access_row_refused(self):
        self.env["im.mcp.access"].search([("model_name", "=", "im.product")]).unlink()
        with self.assertRaises(AccessError):
            tools.draft_stock_move(self.c_env, product_id=self.product.id, quantity=1, dest_id=self.location.id)

    def test_non_positive_quantity_rejected(self):
        with self.assertRaises(UserError):
            tools.draft_stock_move(self.c_env, product_id=self.product.id, quantity=0, dest_id=self.location.id)

    def test_valid_call_creates_draft_move(self):
        result = tools.draft_stock_move(self.c_env, product_id=self.product.id, quantity=5, dest_id=self.location.id)
        move = self.env["im.move"].browse(result["id"])
        self.assertEqual(move.state, "draft")
        self.assertEqual(move.quantity, 5)


class TestApiLogging(McpToolsBase):
    def test_refused_call_is_logged(self):
        self._revoke("im.product")  # ensure no access rule at all -> refused
        user = self._create_role_user("Mcp Log User", "mcp_log_user@test.com", "user")
        connector = self.env["im.mcp.connector"].create({"name": "C", "user_id": user.id})
        c_env = self.env(user=user)

        body = json.dumps(
            {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/call",
                "params": {"name": "search_records", "arguments": {"model": "im.product"}},
            }
        )
        before = self.env["im.api.log"].sudo().search_count([])
        protocol.dispatch(body.encode(), c_env, connector)
        self.assertEqual(self.env["im.api.log"].sudo().search_count([]), before + 1)
        last_log = self.env["im.api.log"].sudo().search([], order="id desc", limit=1)
        self.assertFalse(last_log.allowed)
