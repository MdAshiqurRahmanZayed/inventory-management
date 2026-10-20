import json

from odoo.addons.im_mcp.controllers.im_mcp_endpoint import ImMcpController
from odoo.addons.im_mcp.controllers.im_mcp_endpoint import resolve_user_id
from odoo.addons.inventory_management.tests.common import BaseTransactionCase


class TestMcpAuth(BaseTransactionCase):
    def setUp(self):
        super().setUp()
        self.user = self._create_role_user("Mcp Auth", "mcp_auth@test.com", "user")

    def _generate_key(self, user):
        return self.env["res.users.apikeys"].with_user(user).sudo()._generate(None, "test key", None)

    def test_valid_key_resolves_user(self):
        key = self._generate_key(self.user)
        self.assertEqual(resolve_user_id(self.env, key), self.user.id)

    def test_invalid_key_resolves_nothing(self):
        self.assertFalse(resolve_user_id(self.env, "not-a-real-key"))

    def test_user_without_gate_group_is_blocked(self):
        self.assertFalse(self.user.has_group("im_mcp.group_mcp_user"))
        mcp_group = self.env.ref("im_mcp.group_mcp_user")
        self.user.write({"group_ids": [(4, mcp_group.id)]})
        self.assertTrue(self.user.has_group("im_mcp.group_mcp_user"))

    def test_refusal_without_a_connector_is_still_logged(self):
        before = self.env["im.api.log"].sudo().search_count([])
        ImMcpController._log_refusal(self.env, None, "Invalid API key")
        self.assertEqual(self.env["im.api.log"].sudo().search_count([]), before + 1)
        last_log = self.env["im.api.log"].sudo().search([], order="id desc", limit=1)
        self.assertFalse(last_log.connector_id)
        self.assertFalse(last_log.allowed)


class TestMcpProtocol(BaseTransactionCase):
    def setUp(self):
        super().setUp()
        self.user = self._create_role_user("Mcp Proto", "mcp_proto@test.com", "manager")
        self.connector = self.env["im.mcp.connector"].create(
            {"name": "Test Connector", "user_id": self.user.id}
        )

    def test_initialize_round_trip(self):
        from ..services import protocol

        body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}})
        response = json.loads(protocol.dispatch(body.encode(), self.env, self.connector))
        self.assertEqual(response["result"]["serverInfo"]["name"], protocol.SERVER_NAME)

    def test_tools_call_round_trip(self):
        from ..services import protocol

        body = json.dumps(
            {"jsonrpc": "2.0", "id": 2, "method": "tools/call", "params": {"name": "list_models", "arguments": {}}}
        )
        response = json.loads(protocol.dispatch(body.encode(), self.env, self.connector))
        self.assertIn("content", response["result"])

    def test_unexpected_exception_returns_safe_internal_error(self):
        """A missing required tool argument raises a plain TypeError, not one of the SAFE_ERRORS."""
        from ..services import protocol

        body = json.dumps(
            {"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {"name": "search_records", "arguments": {}}}
        )
        response = json.loads(protocol.dispatch(body.encode(), self.env, self.connector))
        self.assertEqual(response["error"]["code"], -32603)
        self.assertNotIn("TypeError", response["error"]["message"])
