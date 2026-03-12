from odoo import api, models, fields, _

class ResCountryState(models.Model):
    _inherit = 'res.country.state'

    @api.model
    def action_change_state_code(self):
        all_states = self.search([])
        for state in all_states:
            if state.name:
                state.code = state.name