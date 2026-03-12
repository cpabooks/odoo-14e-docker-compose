from odoo import api, models, fields, _

class AccountSoaReport(models.TransientModel):
    _name = 'account.soa.report'
    _description = 'Account SOA Report'

    date = fields.Date('Date', default=fields.date.today())

    def action_print_pdf(self):
        print('clicked')