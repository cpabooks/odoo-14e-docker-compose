from odoo import  api, models, fields, _

class AccountPayment(models.Model):
    _inherit = 'account.payment'

    certificate_id = fields.Many2one('payment.certificate', 'Certificate')