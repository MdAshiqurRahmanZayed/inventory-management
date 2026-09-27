from odoo import api
from odoo import fields
from odoo import models


class ResPartner(models.Model):
    _inherit = "res.partner"

    partner_role = fields.Selection(
        [("supplier", "Supplier"), ("customer", "Customer"), ("both", "Both")],
        string="Business Role",
    )
    is_supplier = fields.Boolean(compute="_compute_roles", store=True)
    is_customer = fields.Boolean(compute="_compute_roles", store=True)

    @api.depends("partner_role")
    def _compute_roles(self):
        for partner in self:
            partner.is_supplier = partner.partner_role in ("supplier", "both")
            partner.is_customer = partner.partner_role in ("customer", "both")
