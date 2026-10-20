"""JSON-RPC 2.0 envelope helpers. Spec: https://www.jsonrpc.org/specification

Error codes -32700..-32603 are reserved by the spec; -32000..-32099 is the
"server error" band reserved for implementation-defined errors.
"""

import json

PARSE_ERROR = -32700
INVALID_REQUEST = -32600
METHOD_NOT_FOUND = -32601
INVALID_PARAMS = -32602
INTERNAL_ERROR = -32603
SERVER_ERROR = -32001


def to_json(payload):
    return json.dumps(payload)


def success(request_id, result):
    return {"jsonrpc": "2.0", "id": request_id, "result": result}


def error(request_id, code, message, data=None):
    err = {"code": code, "message": message}
    if data is not None:
        err["data"] = data
    return {"jsonrpc": "2.0", "id": request_id, "error": err}
