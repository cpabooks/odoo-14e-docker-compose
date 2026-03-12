from odoo import fields, models


class HrContract(models.Model):
    _inherit = 'hr.contract'

    state = fields.Selection([
        ('draft', 'New'),
        ('open', 'Running'),
        ('close', 'Expired'),
        ('cancel', 'Cancelled')
    ], string='Status', group_expand='_expand_states', copy=False,
        tracking=True, help='Status of the contract', default='open')
