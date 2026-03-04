from odoo import api, fields, models
from odoo.exceptions import UserError

class SaasContract(models.Model):
    _inherit = "saas.contract"

    active = fields.Boolean('Active', default=True, copy=True)

    def toggle_active(self):
        return super(SaasContract, self).toggle_active()