from odoo import api, models, fields, _
from datetime import date


class PaymentCertificateWizard(models.TransientModel):
    _name = 'payment.certificate.wizard'
    _description = 'Payment Certificate Wizard'

    def _journal_domain(self):
        domain = []
        company_domain = ('company_id', '=', self.env.company.id)
        vals_domain = ('type', 'in', ('bank', 'cash'))
        domain.append(company_domain)
        domain.append(vals_domain)
        return domain

    company_id = fields.Many2one('res.company', 'Company')
    journal_id = fields.Many2one('account.journal', 'Journal', domain=_journal_domain)
    cheque_no = fields.Char('Cheque No.')
    cheque_date = fields.Date('Cheque Deposit Date.', default=fields.Date.today)
    client_bank = fields.Char('Client Bank Name')
    payment_date = fields.Date('Payment Date', default=fields.Date.today)
    narration = fields.Text('Narration')
    memo = fields.Char('Memo')
    invoice_ids = fields.Many2many(
        'account.move',  # Target model: 'account.move'
        'payment_certificate_invoice_rel',  # Association table
        'wizard_id',  # Column in the association table for the wizard
        'invoice_id',  # Column in the association table for the invoice
        string='Invoices'
    )

    @api.model
    def default_get(self, fields_list):
        res = super(PaymentCertificateWizard, self).default_get(fields_list)
        journal_id = self.env['account.journal'].search([
            ('type', 'in', ('bank', 'cash')),
            ('company_id', '=', self.env.company.id)
        ], limit=1)
        res.update({
            'journal_id': journal_id.id if journal_id else False,
            'company_id': self.env.company.id
        })
        return res

    def action_create_payment_certificate(self):
        # Group invoices by partner_id
        payment_certificates = []
        partner_invoices = {}
        for invoice in self.invoice_ids:
            partner_id = invoice.partner_id
            if partner_id not in partner_invoices:
                partner_invoices[partner_id] = []
            partner_invoices[partner_id].append(invoice)

        # Create payment certificates for each partner
        for partner_id, invoices in partner_invoices.items():
            # Prepare values for the payment certificate
            vals = {
                'partner_id': partner_id.id,
                'company_id': self.company_id.id,
                'journal_id': self.journal_id.id,
                'cheque_no': self.cheque_no,
                'cheque_date': self.cheque_date,
                'client_bank': self.client_bank,
                'date': self.payment_date,
                # 'payment_date': self.payment_date,
                'narration': self.narration,
                'payment_type': 'inbound' if partner_id.customer_rank >= 1 else 'outbound',  # outbound
                'partner_type': 'customer' if partner_id.customer_rank >= 1 else 'supplier',  # outbound
                'amount': sum(invoice.amount_total for invoice in invoices),
                # Assuming payment is for the total invoice amount
                'currency_id': invoices[0].currency_id.id,  # Use currency of first invoice
            }
            payment_certificate = self.env['payment.certificate'].create(vals)

            # Create CertificateInvLine for each invoice
            invoice_names = []
            for invoice in invoices:
                invoice_names.append(invoice.name)
                self.env['certificate.inv.line'].create({
                    'certificate_id': payment_certificate.id,
                    'invoice_id': invoice.id,
                    # 'account_id': invoice.account_id.id,
                    'date': invoice.invoice_date,
                    'date_due': invoice.invoice_date_due,
                    'original_amount': invoice.amount_total,
                    'balance_amount': invoice.amount_residual,
                    'allocation': 0.0,  # This can be calculated or set later
                    'deff_amount': invoice.amount_residual,
                    'currency_id': invoice.currency_id.id
                })
            payment_certificate.ref = ', '.join(invoice_names)
            payment_certificates.append(payment_certificate.id)

        if len(payment_certificates) >= 2:
            return {
                'name': 'Payment Certificates',
                'type': 'ir.actions.act_window',
                'res_model': 'payment.certificate',
                'view_mode': 'tree,form',
                'target': 'current',
                'context': {
                    'group_by': 'partner_id',
                },
                'domain': [
                    ('id', 'in', payment_certificates)
                ]
            }
        else:
            # Optionally return a message or view
            return {
                'name': 'Payment Certificates',
                'type': 'ir.actions.act_window',
                'res_model': 'payment.certificate',
                'view_mode': 'form',
                'target': 'current',
                'res_id': payment_certificate.id,
            }
