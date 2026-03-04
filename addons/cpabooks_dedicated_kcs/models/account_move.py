from odoo import fields, models,api


class AccountMove(models.Model):
    _inherit = 'account.move'

    currency_rate=fields.Float(related="currency_id.rate",string="Currency Rate")
    total_in_aed=fields.Monetary(compute="get_total_in_aed",string="Total In AED")

    bank_details = fields.Many2many('bank.details', string="Bank Details",  default=lambda self:self.get_default_bank())
    # domain = "[('id','in',demo_bank_details)]",

    # demo_bank_details = fields.Many2many('bank.details', compute="_get_bank_details")
    amount_paid = fields.Monetary('Total Paid', currency_field='currency_id')

    # note = fields.Text(default=lambda self: self.get_notes())

    # def get_notes(self):
    #     return "We hope our quotation are in line with your requirements & look forward to hear from you\n\n\n\n\nFor," + self.env.company.name

    def action_compute_paid_amt(self):
        invoices = self.env['account.move'].search([
            ('state', '=', 'posted')
        ])
        for inv in invoices:
            inv.amount_paid = inv.amount_total - inv.amount_residual
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Success',
                'message': f'Computed amounts for {len(invoices)} Invoices',
                'type': 'success',
                'sticky': False,
            }
        }

    def get_default_bank(self):
        company_id = self.env['res.company']._company_default_get()
        bank_details=company_id.bank_details
        return [(6, 0, bank_details.ids)]

    # @api.depends("partner_id")
    # def _get_bank_details(self):
    #     for rec in self:
    #         rec.demo_bank_details = rec.company_id.bank_details.ids
    #         # rec.bank_details = rec.company_id.bank_details.ids

    def get_total_in_aed(self):
        for rec in self:
            rec.total_in_aed=rec.amount_total/rec.currency_rate


