from odoo import api, models, fields, _

class BulkInvPayment(models.TransientModel):
    _inherit = 'bulk.inv.payment'

    certificate_id = fields.Many2one('payment.certificate', 'Certificate')

    @api.model
    def default_get(self, fields_list):
        res = super(BulkInvPayment, self).default_get(fields_list)
        certificate_id = self.env.context.get('certificate_id')
        if certificate_id:
            res['certificate_id'] = certificate_id
        return res

    @api.depends('certificate_id')
    @api.onchange('certificate_id')
    def on_change_certificate_id(self):
        self.ensure_one()
        if self.certificate_id:
            for line in self.certificate_id.adv_line_ids:
                vals = {
                    'paid_amount': line.allocation
                }
                inv_line = self.invoice_ids.browse(line.id)[0]
                print(inv_line)
                print(line.allocation)
                if inv_line:
                    inv_line.paid_amount = line.allocation
                    print(inv_line.paid_amount)