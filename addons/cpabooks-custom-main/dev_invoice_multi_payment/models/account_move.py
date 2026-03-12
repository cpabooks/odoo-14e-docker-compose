from odoo import api, models, fields, _

class AccountMove(models.Model):
    _inherit = 'account.move'

    def acton_launch_multipayment(self):

        return {
                'name': 'Register Payment',
                'type': 'ir.actions.act_window',
                'res_model': 'bulk.inv.payment',
                'view_mode': 'form',
                'target': 'new',
        }