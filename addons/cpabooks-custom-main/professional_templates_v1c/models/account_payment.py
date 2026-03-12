from odoo import api, models, fields, _


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    so_id = fields.Many2one('sale.order', 'Sales Order')