from odoo import api, models, fields, _
from odoo.api import depends
from odoo.exceptions import UserError, ValidationError


class PaymentCertificate(models.Model):
    _name = 'payment.certificate'
    _inherit = ['mail.thread', 'sequence.mixin']
    _description = 'Payment Certificate'
    _rec_name = 'name'

    def _journal_domain(self):
        domain = []
        company_domain = ('company_id', '=', self.env.company.id)
        vals_domain = ('type', 'in', ('bank', 'cash'))
        domain.append(company_domain)
        domain.append(vals_domain)
        return domain

    def _company_domain(self):
        domain = [
            ('company_id', '=', self.env.company.id)
        ]
        return domain

    @api.depends('amount')
    def _get_num_word(self):
        for rec in self:
            rec.num_word = ''
            currency_id = rec.currency_id if rec.currency_id else self.env.company.currency_id
            if rec.currency_id:
                rec.num_word = str(currency_id.amount_to_text(rec.amount))

    company_id = fields.Many2one('res.company', 'Company', readonly=True, default=lambda self: self.env.company.id,
                                 index=True, tracking=True)
    name = fields.Char('name', tracking=True)
    payment_type = fields.Selection([
        ('outbound', 'Send Money'),
        ('inbound', 'Receive Money')
    ], 'Payment Type', tracking=True)
    partner_type = fields.Selection([
        ('customer', 'Customer'),
        ('supplier', 'Vendor'),
    ], tracking=True)
    currency_id = fields.Many2one('res.currency', 'Currency', default=lambda self: self.env.company.currency_id.id,
                                  tracking=True)
    partner_id = fields.Many2one('res.partner', 'Customer/Vendor', required=True,
                                 domain=[('supplier_rank', '>=', 1), ('supplier_invoice_count', '>=', 1)],
                                 tracking=True)
    destination_account_id = fields.Many2one('account.account', 'Destination Account', tracking=True)
    is_internal_transfer = fields.Boolean('Is Internal Transfer', default=False, tracking=True)
    journal_id = fields.Many2one('account.journal', 'Journal', required=True, domain=_journal_domain, tracking=True)
    allocation_amount = fields.Float('Total Amount', tracking=True)
    narration = fields.Text('Narration', tracking=True)
    amount = fields.Float('Amount', default=0.0, tracking=True)
    date = fields.Date('Date', default=fields.Date.today, tracking=True)
    cheque_no = fields.Char('Check Ref No.', tracking=True)
    cheque_date = fields.Date('Cheque Deposit Date', tracking=True)
    ref = fields.Char('Memo', tracking=True)
    adv_line_ids = fields.One2many('certificate.inv.line', 'certificate_id', 'Payment Item')
    previous_balance = fields.Float('Previous Balance', default=0.0, tracking=True)
    other_dedication = fields.Float(' Other Deduction', default=0.0, tracking=True)
    deduction_reason = fields.Text('Reason', tracking=True)
    num_word = fields.Char('Amount in Word', compute=_get_num_word)
    prepared_by = fields.Many2one('hr.employee', 'Prepared By.', tracking=True)
    approve_by = fields.Many2one('hr.employee', 'Approved By.', tracking=True)
    checked_by = fields.Many2one('hr.employee', 'Checked By.', tracking=True)
    woff_amount = fields.Float('Write-off Amount', tracking=True)
    woff_account = fields.Many2one('account.account', 'Write-off Account', domain=_company_domain, tracking=True)
    woff_label = fields.Char('Write-off Label', tracking=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('approved', 'Approved'),
        ('registered', 'Register Payment'),
        ('cancel', 'Canceled')
    ], 'State', default='draft', tracking=True)
    payment_id = fields.Many2one('account.payment', 'Payment')
    payment_ref = fields.Char('Payment Ref. No.')

    def action_view_payment(self):
        self.ensure_one()
        return {
            'name': 'Payments',
            'type': 'ir.actions.act_window',
            'model': 'ir.actions.act_window',
            'res_model': 'account.payment',
            'view_mode': 'form',
            'res_id': self.payment_id.id,
            'target': 'current'
        }

    @api.model
    def default_get(self, fields_list):
        res = super(PaymentCertificate, self).default_get(fields_list)
        journal_id = self.env['account.journal'].search([
            ('type', 'in', ('bank', 'cash'))
        ], order='id asc', limit=1)
        woff_account = self.env['account.account'].search([
            ('name', 'ilike', 'Write off')
        ], limit=1)
        res.update({
            'woff_account': woff_account.id or False,
            'journal_id': journal_id.id or False
        })
        return res

    def action_approve(self):
        self.ensure_one()
        self._remove_lines()
        self.state = 'approved'

    def create_register_vals(self):
        vals = {
            'payment_type': self.payment_type,
            'partner_type': self.partner_type,
            'partner_id': self.partner_id.id,
            'currency_id': self.currency_id.id,
            'certificate_id': self.id,
            'payment_for': 'multi_payment',
            'amount': self.amount,
            'date': self.date,
            'ref': self.ref,
            'narration': self.narration,
            'adv_line_ids': [
                (0, 0, {
                    'invoice_id': line.invoice_id.id,
                    'project_id': line.project_id.id,
                    'date': line.date,
                    'original_amount': line.original_amount,
                    'balance_amount': line.balance_amount,
                    'allocation': line.allocation,
                    'woff_amount': line.woff_amount,
                    'woff_account': line.woff_account.id if line.woff_account else False,
                    'woff_label': line.woff_label,
                }) for line in self.adv_line_ids
            ]
        }
        woff_amount = 0.0
        woff_account = False
        if self.other_dedication:
            woff_amount = self.woff_amount + self.other_dedication
        if woff_amount != 0.0:
            woff_account = self.woff_account
        vals.update({
            'woff_amount': woff_amount,
            'woff_account': woff_account.id if woff_account else False,
            'woff_label': self.woff_label if self.woff_label else self.deduction_reason if self.deduction_reason else 'Write-Off',
        })
        return vals

    def _remove_lines(self):
        line_ids = self.adv_line_ids.filtered(lambda line: line.allocation == 0.0)
        line_ids.unlink()

    def action_register_payment(self):
        self.ensure_one()
        if self.other_dedication or self.woff_amount:
            # TODO: Get total write-off amount from adv line and match the value with self.woff_amount
            total_woff_amount = sum([line.woff_amount for line in self.adv_line_ids.filtered(lambda i: i.allocation != 0) if line])
            print(total_woff_amount)
            if total_woff_amount != (self.other_dedication + self.woff_amount):
                raise ValidationError(_('Please match the "Write-off Amount" for lines.'))

        return {
            'name': 'Register Payment',
            'res_model': 'certificate.payment.wizard',
            'type': 'ir.actions.act_window',
            'model': 'ir.actions.act_window',
            'view_mode': 'form',
            'target': 'new',
            'view_id': self.env.ref('cpabooks_dedicated_alhilal.certificate_payment_wizard_form').id
        }
        # vals = self._create_register_vals()
        # if vals:
        #     payment = self.env['account.payment'].create(vals)
        #     self.payment_id = payment.id
        #     self.state = 'registered'

    def action_cancel(self):
        self.state = 'draft'

    @api.depends('adv_line_ids')
    def _compute_amount(self):
        for rec in self:
            amount = 0.0
            if len(rec.adv_line_ids) != 0:
                amount = sum([line.allocation for line in rec.adv_line_ids])
            rec.amount = amount

    @api.model
    def default_get(self, fields_list):
        res = super(PaymentCertificate, self).default_get(fields_list)
        res.update({
            'company_id': self.env.company.id,
            'currency_id': self.env.company.currency_id.id if self.env.company.currency_id else False
        })
        return res

    @api.model
    def create(self, vals):
        res = super(PaymentCertificate, self).create(vals)
        if not res.name:
            res.name = self.env['ir.sequence'].next_by_code('sequence.payment.certificate')
        return res

    def check_report(self):
        data = {
            'form': self  # Pass the current record's ID
        }
        return self.env.ref('cpabooks_dedicated_alhilal.action_report_payment_certificate').report_action(self,
                                                                                                          data=data)

    def _clear_line(self):
        payment_certificates = self.env['certificate.inv.line'].search([
            ('certificate_id', '=', self.id)
        ])
        if payment_certificates:
            payment_certificates.unlink()

    def action_remove_inv_lines(self):
        """clear objects from adv_line_ids"""
        self._clear_line()

    def action_get_inv_lines(self):
        """Create objects for adv_line_ids"""
        self.ensure_one()
        self._clear_line()
        if not self.partner_id:
            raise ValueError(_('Please Select Partner'))
        invoice_ids = self.env['account.move'].search([
            ('partner_id', '=', self.partner_id.id),
            ('amount_residual', '!=', 0.0),
            ('move_type', '=', 'in_invoice'),
            ('state', '=', 'posted')
        ], order="id asc")
        if not invoice_ids:
            raise ValidationError(_('No Due Bills Found for this Vendor'))
        adv_line = self.env['certificate.inv.line']
        total_allocation = 0
        for inv in invoice_ids:
            total_allocation += inv.amount_residual
            vals = {
                'certificate_id': self.id,
                'full_reco': False,
                'invoice_id': inv.id,
                'project_id': inv.project_id.id,
                'date': inv.invoice_date,
                'original_amount': abs(inv.amount_total_signed),
                'balance_amount': inv.amount_residual,
            }

            existing = adv_line.search([
                ('certificate_id', '=', self.id),
                ('invoice_id', '=', inv.id)
            ], limit=1)
            if existing:
                existing.write(vals)
            else:
                adv_line.create(vals)
        self.write({
            'amount': total_allocation
        })


class CertificateInvLine(models.Model):
    _name = 'certificate.inv.line'
    _description = 'Payment Certificate Invoice Line'

    def _company_domain(self):
        domain = [
            ('company_id', '=', self.env.company.id)
        ]
        return domain

    certificate_id = fields.Many2one('payment.certificate', 'Certificate', tracking=True)
    full_reco = fields.Boolean('Full Reco', tracking=True)
    invoice_id = fields.Many2one('account.move', 'Invoice', tracking=True)
    project_id = fields.Many2one('project.project', 'Project', tracking=True)
    date = fields.Date('Date', tracking=True)
    original_amount = fields.Float('Original Amount', tracking=True)
    balance_amount = fields.Float('Balance Amount', tracking=True)
    allocation = fields.Float('Allocation', tracking=True)
    woff_amount = fields.Float('Write-off Amount', tracking=True)
    woff_account = fields.Many2one('account.account', domain=_company_domain, tracking=True)
    woff_label = fields.Char('Label', tracking=True)
    diff_amt = fields.Float('Remaining Amount', default=0.0, compute='_compute_diff_amt')

    @api.onchange('invoice_id')
    def action_invoice_id(self):
        for rec in self:
            if rec.invoice_id and rec.invoice_id.project_id:
                rec.project_id = rec.invoice_id.project_id.id

    @api.onchange('full_reco')
    def action_full_reco(self):
        for rec in self:
            if rec.full_reco:
                rec.allocation = rec.balance_amount
            else:
                rec.full_reco = 0.0

    @api.depends('balance_amount', 'allocation', 'woff_amount')
    def _compute_diff_amt(self):
        for rec in self:
            rec.diff_amt = rec.balance_amount - rec.allocation - rec.woff_amount

    def _calculate_amount(self):
        """Calculate total amount and assign to parent"""
        for rec in self:
            if rec.certificate_id:
                adv_lines = rec.certificate_id.adv_line_ids
                total_amount = sum(line.allocation for line in adv_lines)
                total_allocation = total_amount - sum([line.woff_amount for line in adv_lines])
                rec.certificate_id.write({
                    'amount': total_amount,
                    'allocation_amount': total_amount
                    # 'amount':
                })

    def write(self, vals):
        res = super(CertificateInvLine, self).write(vals)
        if vals.get('allocation'):
            self._calculate_amount()
        return res

    def unlink(self):
        """Calculate total amount and assign to the parent on unlink the object"""
        certificates = self.mapped('certificate_id')  # cache before unlink
        res = super(CertificateInvLine, self).unlink()
        for certificate in certificates:
            adv_lines = certificate.adv_line_ids
            certificate.amount = sum(line.allocation for line in adv_lines)
        return res
