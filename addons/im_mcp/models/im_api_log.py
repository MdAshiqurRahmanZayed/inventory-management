from odoo import fields
from odoo import models


class ImApiLog(models.Model):
    _name = "im.api.log"
    _description = "MCP API Call Log"
    _order = "id desc"

    connector_id = fields.Many2one("im.mcp.connector", help="Empty when the request never resolved to a connector (e.g. a bad API key).")
    user_id = fields.Many2one("res.users", string="Resolved User")
    tool = fields.Char(required=True)
    model = fields.Char()
    operation = fields.Char()
    inputs = fields.Text()
    result = fields.Text()
    allowed = fields.Boolean()
    duration = fields.Float(help="Call duration in seconds.")

    @staticmethod
    def log_call(env, connector, user, tool, model, operation, inputs, result, allowed, duration):
        env["im.api.log"].sudo().create(
            {
                "connector_id": connector.id if connector else False,
                "user_id": user.id if user else False,
                "tool": tool,
                "model": model or "",
                "operation": operation or "",
                "inputs": str(inputs) if inputs is not None else "",
                "result": str(result) if result is not None else "",
                "allowed": allowed,
                "duration": duration,
            }
        )
