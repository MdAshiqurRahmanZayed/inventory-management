import json
import logging
import time

from odoo.addons.im_mcp.services import jsonrpc
from odoo.addons.im_mcp.services import tools as tools_mod
from odoo.exceptions import AccessError
from odoo.exceptions import MissingError
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)

SAFE_ERRORS = (AccessError, MissingError, UserError, ValidationError)

SERVER_NAME = "inventory-mcp"
SERVER_VERSION = "1.0.0"
PROTOCOL_VERSION = "2025-03-26"


def _call_tool(env, connector, name, args):
    func = tools_mod.TOOLS.get(name)
    if func is None:
        raise UserError(f"Unknown tool: {name}")

    start = time.time()
    allowed = True
    result = None
    try:
        result = func(env, **args)
    except Exception:
        allowed = False
        raise
    finally:
        env["im.api.log"].log_call(
            env, connector, env.user, name, args.get("model"), name,
            args, result, allowed, time.time() - start,
        )
    return result


def dispatch(raw_body, env, connector):
    """Handle one JSON-RPC message. Returns a JSON string, or None for a notification."""
    try:
        message = json.loads(raw_body)
    except ValueError:
        return jsonrpc.to_json(jsonrpc.error(None, jsonrpc.PARSE_ERROR, "Parse error"))

    request_id = message.get("id")
    method = message.get("method")
    params = message.get("params") or {}

    if method == "initialize":
        return jsonrpc.to_json(
            jsonrpc.success(
                request_id,
                {
                    "protocolVersion": PROTOCOL_VERSION,
                    "serverInfo": {"name": SERVER_NAME, "version": SERVER_VERSION},
                    "capabilities": {"tools": {}},
                },
            )
        )

    if method == "tools/list":
        tool_list = [
            {
                "name": name,
                "description": (func.__doc__ or name).strip(),
                "inputSchema": tools_mod.TOOL_SCHEMAS.get(name, {"type": "object"}),
            }
            for name, func in tools_mod.TOOLS.items()
        ]
        return jsonrpc.to_json(jsonrpc.success(request_id, {"tools": tool_list}))

    if method == "tools/call":
        name = params.get("name")
        args = params.get("arguments") or {}
        try:
            result = _call_tool(env, connector, name, args)
        except SAFE_ERRORS as exc:
            return jsonrpc.to_json(jsonrpc.error(request_id, jsonrpc.SERVER_ERROR, str(exc)))
        except Exception:
            _logger.exception("MCP tool '%s' failed unexpectedly", name)
            return jsonrpc.to_json(jsonrpc.error(request_id, jsonrpc.INTERNAL_ERROR, "Internal error"))
        return jsonrpc.to_json(
            jsonrpc.success(request_id, {"content": [{"type": "text", "text": json.dumps(result, default=str)}]})
        )

    if request_id is None:
        return None
    return jsonrpc.to_json(jsonrpc.error(request_id, jsonrpc.METHOD_NOT_FOUND, f"Unknown method: {method}"))
