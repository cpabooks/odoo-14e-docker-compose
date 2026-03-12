from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

ONBOARDING_STEP_STATES = [
    ('not_done', "Not done"),
    ('just_done', "Just done"),
    ('done', "Done"),
]
DASHBOARD_ONBOARDING_STATES = ONBOARDING_STEP_STATES + [('closed', 'Closed')]

class DailySiteReport(models.Model):
    _inherit = "res.company"

    account_dashboard_onboarding_state = fields.Selection(DASHBOARD_ONBOARDING_STATES,
                                                          string="State of the account dashboard onboarding panel",
                                                          default='closed')

    @api.model
    def action_closed_onboard_config_panel_from_acc_dashboard(self):
        all_company=self.env['res.company'].sudo().search([])
        for rec in all_company:
            rec.account_dashboard_onboarding_state='closed'



