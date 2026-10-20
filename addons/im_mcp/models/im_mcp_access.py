from odoo import api
from odoo import fields
from odoo import models
from odoo.exceptions import ValidationError

BLOCKED_MODEL_PREFIXES = ("ir.", "im.mcp.")
BLOCKED_MODELS = ("res.users", "im.api.log")


class ImMcpAccess(models.Model):
    _name = "im.mcp.access"
    _description = "MCP Access Rule"
    _order = "model_name"
    _rec_name = "model_id"

    model_id = fields.Many2one("ir.model", string="Model", required=True, ondelete="cascade")
    model_name = fields.Char(string="Technical Model Name", related="model_id.model", store=True, readonly=True)
    enabled = fields.Boolean(default=True, help="When disabled, this model is not reachable through MCP at all.")
    can_read = fields.Boolean(default=True)
    can_write = fields.Boolean()
    can_create = fields.Boolean()
    can_delete = fields.Boolean()
    field_ids = fields.Many2many(
        "ir.model.fields", string="Allowed Fields", domain="[('model_id', '=', model_id)]"
    )
    domain = fields.Char(help="Extra domain applied to every search/read through this rule.")
    max_records = fields.Integer(default=100)

    _model_uniq = models.Constraint("unique(model_id)", "An access rule for this model already exists.")

    @api.constrains("model_name")
    def _check_model_not_sensitive(self):
        for access in self:
            name = access.model_name or ""
            if name in BLOCKED_MODELS or name.startswith(BLOCKED_MODEL_PREFIXES):
                raise ValidationError(
                    f"Model '{name}' cannot be exposed through an MCP connector."
                )

    @api.constrains("field_ids", "model_id")
    def _check_fields_belong_to_model(self):
        for access in self:
            foreign = access.field_ids.filtered(lambda f: f.model_id != access.model_id)
            if foreign:
                raise ValidationError(
                    f"These fields don't belong to '{access.model_name}': {', '.join(foreign.mapped('name'))}."
                )

    OPERATION_FIELDS = {
        "read": "can_read",
        "write": "can_write",
        "create": "can_create",
        "delete": "can_delete",
    }

    @api.model
    def get_access(self, model_name, operation):
        """Return the enabled access rule granting *operation* on *model_name*, or None."""
        field = self.OPERATION_FIELDS[operation]
        access = self.sudo().search([("model_name", "=", model_name), ("enabled", "=", True)], limit=1)
        if access and access[field]:
            return access
        return None

    @api.model
    def get_enabled_models_info(self):
        """List of dicts describing every enabled model and its allowed operations."""
        rules = self.sudo().search([("enabled", "=", True)], order="model_name")
        return [
            {
                "model": rule.model_name,
                "operations": {
                    "read": rule.can_read,
                    "write": rule.can_write,
                    "create": rule.can_create,
                    "delete": rule.can_delete,
                },
            }
            for rule in rules
        ]
