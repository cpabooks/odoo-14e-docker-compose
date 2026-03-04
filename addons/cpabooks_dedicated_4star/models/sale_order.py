from odoo import api, models, fields, _


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    payment_mode = fields.Many2one('account.payment.method', 'Payment Mode')

    def _create_invoices(self, grouped=False, final=False):
        res = super(SaleOrder, self)._create_invoices(grouped=grouped, final=final)
        for invoice in self.mapped('invoice_ids'):
            invoice.payment_mode = self.payment_mode.id if self.payment_mode else False
        return res
