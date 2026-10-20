import ast
import json

from odoo.exceptions import AccessError
from odoo.exceptions import MissingError
from odoo.exceptions import UserError


def _parse_domain(domain_str):
    if not domain_str:
        return []
    return ast.literal_eval(domain_str)


def _parse_fields(value):
    """Accept a list, a JSON-encoded list, or None."""
    if value is None:
        return None
    if isinstance(value, list):
        return value
    if isinstance(value, str):
        try:
            parsed = json.loads(value)
        except ValueError:
            raise UserError(f"fields must be a list, got: {value!r}")
        if not isinstance(parsed, list):
            raise UserError(f"fields must be a list, got: {value!r}")
        return parsed
    raise UserError(f"fields must be a list, got: {value!r}")


def _as_int(value, name):
    """MCP clients may send numbers as strings; coerce defensively instead of crashing."""
    try:
        return int(value)
    except (TypeError, ValueError):
        raise UserError(f"{name} must be an integer, got: {value!r}")


def _as_float(value, name):
    try:
        return float(value)
    except (TypeError, ValueError):
        raise UserError(f"{name} must be a number, got: {value!r}")


def _check_access(env, model, operation):
    access = env["im.mcp.access"].get_access(model, operation)
    if access is None:
        raise AccessError(
            f"MCP is not allowed to '{operation}' on '{model}'. "
            f"Ask a Manager to enable it: MCP Connector app > Access Rules > '{model}' > tick '{operation}'."
        )
    return access


def _parse_values(value):
    """Accept a dict, a JSON-encoded dict, or raise."""
    if isinstance(value, dict):
        return value
    if isinstance(value, str):
        try:
            parsed = json.loads(value)
        except ValueError:
            raise UserError(f"values must be an object, got: {value!r}")
        if not isinstance(parsed, dict):
            raise UserError(f"values must be an object, got: {value!r}")
        return parsed
    raise UserError(f"values must be an object, got: {value!r}")


def _fields_for(access, requested=None):
    allowed = access.field_ids.mapped("name")
    requested = _parse_fields(requested)
    if not allowed:
        return requested
    if requested is None:
        return allowed
    return [f for f in requested if f in allowed]


def search_records(env, model, domain=None, fields=None, limit=10, offset=0):
    access = _check_access(env, model, "read")
    if access.max_records == 0:
        return {"records": [], "count": 0}
    limit = _as_int(limit, "limit") if limit is not None else access.max_records
    offset = _as_int(offset, "offset") if offset is not None else 0
    limit = min(limit or access.max_records, access.max_records)
    combined_domain = _parse_domain(access.domain) + (domain or [])
    records = env[model].search(combined_domain, limit=limit, offset=offset)
    return {"records": records.read(_fields_for(access, fields)), "count": len(records)}


def _record_exists(env, model, record_id):
    """True if record_id exists in model, respecting MCP's read access and the user's own record rules."""
    _check_access(env, model, "read")
    return bool(env[model].search([("id", "=", record_id)], limit=1))


def get_record(env, model, record_id, fields=None):
    access = _check_access(env, model, "read")
    record_id = _as_int(record_id, "record_id")
    record = env[model].browse(record_id)
    if not record.exists():
        raise MissingError(f"Record not found: {model}/{record_id}")
    return {"record": record.read(_fields_for(access, fields))[0]}


def create_record(env, model, values):
    _check_access(env, model, "create")
    record = env[model].create(_parse_values(values))
    return {"id": record.id}


def update_record(env, model, record_id, values):
    _check_access(env, model, "write")
    record_id = _as_int(record_id, "record_id")
    record = env[model].browse(record_id)
    if not record.exists():
        raise MissingError(f"Record not found: {model}/{record_id}")
    record.write(_parse_values(values))
    return {"id": record_id}


def delete_record(env, model, record_id):
    _check_access(env, model, "delete")
    record_id = _as_int(record_id, "record_id")
    record = env[model].browse(record_id)
    if not record.exists():
        raise MissingError(f"Record not found: {model}/{record_id}")
    record.unlink()
    return {"deleted_id": record_id}


def list_models(env):
    """List every model enabled for MCP, with its allowed operations."""
    return {"models": env["im.mcp.access"].get_enabled_models_info()}


def draft_stock_move(env, product_id, quantity, source_id=None, dest_id=None):
    _check_access(env, "im.move", "create")
    product_id = _as_int(product_id, "product_id")
    quantity = _as_float(quantity, "quantity")
    source_id = _as_int(source_id, "source_id") if source_id else None
    dest_id = _as_int(dest_id, "dest_id") if dest_id else None
    if quantity <= 0:
        raise UserError(f"Quantity must be positive: {quantity}")
    if not _record_exists(env, "im.product", product_id):
        raise UserError(f"Product not found: {product_id}")
    if source_id and not _record_exists(env, "im.location", source_id):
        raise UserError(f"Source location not found: {source_id}")
    if dest_id and not _record_exists(env, "im.location", dest_id):
        raise UserError(f"Destination location not found: {dest_id}")
    if not source_id and not dest_id:
        raise UserError("A stock move needs at least a source or a destination location.")
    move = env["im.move"].create(
        {
            "product_id": product_id,
            "quantity": quantity,
            "source_id": source_id,
            "dest_id": dest_id,
        }
    )
    return {"id": move.id, "state": move.state}


TOOLS = {
    "search_records": search_records,
    "get_record": get_record,
    "create_record": create_record,
    "update_record": update_record,
    "delete_record": delete_record,
    "list_models": list_models,
    "draft_stock_move": draft_stock_move,
}

_MODEL_PROP = {"type": "string", "description": "Technical model name, e.g. 'im.product'."}
_RECORD_ID_PROP = {"type": "integer"}

TOOL_SCHEMAS = {
    "search_records": {
        "type": "object",
        "properties": {
            "model": _MODEL_PROP,
            "domain": {"type": "array", "description": "Odoo domain, e.g. [[\"name\", \"=\", \"Widget\"]]."},
            "fields": {"type": "array", "items": {"type": "string"}},
            "limit": {"type": "integer", "default": 10},
            "offset": {"type": "integer", "default": 0},
        },
        "required": ["model"],
    },
    "get_record": {
        "type": "object",
        "properties": {
            "model": _MODEL_PROP,
            "record_id": _RECORD_ID_PROP,
            "fields": {"type": "array", "items": {"type": "string"}},
        },
        "required": ["model", "record_id"],
    },
    "create_record": {
        "type": "object",
        "properties": {"model": _MODEL_PROP, "values": {"type": "object"}},
        "required": ["model", "values"],
    },
    "update_record": {
        "type": "object",
        "properties": {"model": _MODEL_PROP, "record_id": _RECORD_ID_PROP, "values": {"type": "object"}},
        "required": ["model", "record_id", "values"],
    },
    "delete_record": {
        "type": "object",
        "properties": {"model": _MODEL_PROP, "record_id": _RECORD_ID_PROP},
        "required": ["model", "record_id"],
    },
    "list_models": {"type": "object", "properties": {}},
    "draft_stock_move": {
        "type": "object",
        "properties": {
            "product_id": {"type": "integer"},
            "quantity": {"type": "number"},
            "source_id": {"type": "integer"},
            "dest_id": {"type": "integer"},
        },
        "required": ["product_id", "quantity"],
    },
}
