from odoo import fields
from odoo import models


class ImMcpConnector(models.Model):
    _name = "im.mcp.connector"
    _description = "MCP Connector"
    _order = "name"

    name = fields.Char(required=True)
    user_id = fields.Many2one("res.users", string="Runs As", required=True)
    active = fields.Boolean(default=True)
    expires_on = fields.Date()
    rate_limit = fields.Integer(string="Rate Limit (calls/min)")
    last_used = fields.Datetime(readonly=True)

    def is_usable(self):
        self.ensure_one()
        if not self.active:
            return False
        if self.expires_on and self.expires_on < fields.Date.today():
            return False
        return True
