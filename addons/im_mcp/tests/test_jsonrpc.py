import json

from odoo.addons.im_mcp.services import jsonrpc
from odoo.tests.common import TransactionCase


class TestJsonRpcEnvelope(TransactionCase):
    def test_success_envelope(self):
        payload = jsonrpc.success(1, {"ok": True})
        self.assertEqual(payload, {"jsonrpc": "2.0", "id": 1, "result": {"ok": True}})

    def test_error_envelope_without_data(self):
        payload = jsonrpc.error(1, jsonrpc.INVALID_PARAMS, "bad input")
        self.assertEqual(
            payload, {"jsonrpc": "2.0", "id": 1, "error": {"code": jsonrpc.INVALID_PARAMS, "message": "bad input"}}
        )

    def test_error_envelope_with_data(self):
        payload = jsonrpc.error(1, jsonrpc.SERVER_ERROR, "refused", data={"model": "im.product"})
        self.assertEqual(payload["error"]["data"], {"model": "im.product"})

    def test_to_json_round_trips(self):
        payload = jsonrpc.success(2, {"models": ["im.product"]})
        self.assertEqual(json.loads(jsonrpc.to_json(payload)), payload)

    def test_reserved_codes_match_spec(self):
        self.assertEqual(jsonrpc.PARSE_ERROR, -32700)
        self.assertEqual(jsonrpc.INVALID_REQUEST, -32600)
        self.assertEqual(jsonrpc.METHOD_NOT_FOUND, -32601)
        self.assertEqual(jsonrpc.INVALID_PARAMS, -32602)
        self.assertEqual(jsonrpc.INTERNAL_ERROR, -32603)
        self.assertTrue(-32099 <= jsonrpc.SERVER_ERROR <= -32000)
