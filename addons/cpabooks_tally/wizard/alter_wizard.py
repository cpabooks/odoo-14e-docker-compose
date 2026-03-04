from odoo import api, models, fields, _
from odoo.exceptions import UserError


class AlterWizard(models.TransientModel):
    _name = 'alter.wizard'

    ledger_id = fields.Many2one('account.account', 'Choose Account')

    def edit(self):
        if self.ledger_id:
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'account.account',
                'view_type': 'form',
                'view_mode': 'form',
                'target': 'current',
                'res_id': self.ledger_id.id,
                'context': {'default_ledger_id': self.ledger_id.id},
            }
        else:
            raise UserError(_("Please select a Ledger first"))

