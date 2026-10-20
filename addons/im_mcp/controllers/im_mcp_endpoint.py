import json

import odoo
from odoo import http
from odoo.addons.im_mcp.services import jsonrpc
from odoo.addons.im_mcp.services import protocol
from odoo.http import request
from werkzeug.wrappers import Response


def resolve_user_id(env, api_key):
    """Validate api_key against Odoo's own API keys, return the user id or None."""
    return env["res.users.apikeys"].sudo()._check_credentials(scope="rpc", key=api_key)


def _unauthorized(message):
    body = jsonrpc.to_json(jsonrpc.error(None, jsonrpc.SERVER_ERROR, message))
    return Response(body, status=401, headers={"Content-Type": "application/json"})


class ImMcpController(http.Controller):
    @http.route("/mcp/", type="http", auth="none", methods=["POST"], csrf=False)
    def mcp_handler(self, **_kwargs):
        env, error = self._authenticate()
        if error:
            self._log_refusal(request.env, None, error)
            return _unauthorized(error)

        connector = (
            env["im.mcp.connector"]
            .sudo()
            .search([("user_id", "=", env.uid), ("active", "=", True)], limit=1)
        )
        if not connector or not connector.is_usable():
            self._log_refusal(env, None, "No usable connector for this user")
            return _unauthorized("No usable connector for this user")

        raw_body = request.httprequest.get_data()
        response_body = protocol.dispatch(raw_body, env, connector)
        if response_body is None:
            return Response("", status=200, headers={"Content-Type": "application/json"})
        return Response(response_body, status=200, headers={"Content-Type": "application/json"})

    def _authenticate(self):
        httpreq = request.httprequest
        bearer = httpreq.headers.get("Authorization", "")
        api_key = bearer[7:].strip() if bearer.lower().startswith("bearer ") else httpreq.headers.get("X-API-Key", "").strip()
        if not api_key:
            return None, "Missing API key"

        user_id = resolve_user_id(request.env, api_key)
        if not user_id:
            return None, "Invalid API key"

        env = odoo.api.Environment(request.env.cr, user_id, request.env.context)
        if not env.user.has_group("im_mcp.group_mcp_user"):
            return None, "User is not authorised for MCP access"
        return env, None

    @staticmethod
    def _log_refusal(env, connector, message):
        user = env.user if env.uid else None
        env["im.api.log"].sudo().log_call(env, connector, user, "_auth", None, "connect", None, message, False, 0.0)

    @http.route("/mcp/health", type="http", auth="none", methods=["GET"], csrf=False)
    def health(self, **_kwargs):
        status = {"status": "ok", "server": protocol.SERVER_NAME, "version": protocol.SERVER_VERSION}
        return Response(json.dumps(status), status=200, headers={"Content-Type": "application/json"})
