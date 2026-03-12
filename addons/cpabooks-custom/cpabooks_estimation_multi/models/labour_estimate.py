from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError


class LabourEstimate(models.Model):
    _inherit = "labour.estimate"
    _description = "Labour Estimate"

    # @api.one
    @api.constrains('hours')
    def _check_hours(self):
        for rec in self:
            if rec.hours < 0.0:
                raise UserError(_('Working hours should not be negative.'))