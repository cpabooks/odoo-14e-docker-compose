from odoo import models, fields

class UpdateModuleResultWizard(models.TransientModel):
    _name = 'update.module.result.wizard'
    _description = 'Update Module Result Wizard'

    result_message = fields.Text('Result Message', readonly=True)

    def action_close(self):
        return {'type': 'ir.actions.act_window_close'}
