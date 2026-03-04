from odoo import api, models, fields, _


class CertificateInvPayment(models.TransientModel):
    _name = 'certificate.payment.wizard'
    _description = 'Register Payment from Payment Certificate'

    journal_id = fields.Many2one('account.journal', 'Journal', domain=[('type', 'in', ('bank', 'cash'))])
    cheque_no = fields.Char('Cheque No')
    cheque_date = fields.Date('Cheque Date')
    amount = fields.Float('Amount')
    currency_id = fields.Many2one('res.currency')
    payment_date = fields.Date('Payment Date', default=fields.Date.today)
    narration = fields.Text('Narration')
    certificate_id = fields.Many2one('payment.certificate', 'Certificate')

    def action_process(self):
        payment = self.env['account.payment']
        vals = self.certificate_id.create_register_vals()
        if vals:
            vals.update({
                'journal_id': self.journal_id.id,
                'cheque_no': self.cheque_no or '',
                'cheque_date': self.cheque_date or None,
            })
            payment_id = payment.create(vals)
            if payment_id:
                payment_id.dev_generate_moves()
                self.certificate_id.write({
                    'payment_id': payment_id.id,
                    'state': 'registered'
                })

    @api.model
    def default_get(self, fields_list):
        res = super(CertificateInvPayment, self).default_get(fields_list)
        certificate_id = self._context.get('active_ids', '')
        total_amount = 0.0
        certificate = self.env['payment.certificate'].browse(certificate_id)
        journal_id = False
        cheque_no = ''
        cheque_date = None
        if certificate:
            total_amount = sum([line.allocation for line in certificate[0].adv_line_ids])
            journal_id = certificate.journal_id.id
            cheque_no = certificate.cheque_no
            cheque_date = certificate.cheque_date
        journal = self.env['account.journal'].search([
            ('type', 'in', ('bank', 'cash'))
        ], limit=1, order="id asc")

        res.update({
            'amount': total_amount,
            'currency_id': self.env.company.currency_id.id,
            'journal_id': journal_id,
            'certificate_id': certificate.id if certificate else False,
            'cheque_no': cheque_no,
            'cheque_date': cheque_date
        })
        return res
