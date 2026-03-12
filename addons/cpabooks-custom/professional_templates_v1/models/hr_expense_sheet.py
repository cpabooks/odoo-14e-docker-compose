from odoo import api, fields, models, _


class HrExpenseSheet(models.Model):
    _inherit = 'hr.expense'

    partner_id = fields.Many2one('res.partner',string='Partner')