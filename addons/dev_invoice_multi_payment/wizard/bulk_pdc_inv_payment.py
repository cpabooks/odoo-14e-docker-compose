from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
import itertools
from operator import itemgetter
import operator
from datetime import datetime

class bulk_pdc_inv_payment(models.TransientModel):
    _name = 'bulk.pdc.payment'
    _description = 'Bulk pdc invoice payment'

    @api.model
    def default_get(self, fields):
        res = {}
        inv_ids = self._context.get('active_ids')
        vals = []
        invoice_ids = self.env['account.move'].browse(inv_ids)
        inv_type = ''
        for invo in invoice_ids:
            inv_type = invo.move_type
            break
        for inv in invoice_ids:
            if inv_type != inv.move_type:
                raise ValidationError('You must select only invoices or refunds.')
            if inv.state == 'draft' or inv.payment_state == 'paid':
                raise ValidationError('Please Select posted or unpaid invoice...')
            payment_type=""
            if inv.move_type in ('out_invoice', 'out_refund'):
                res.update({
                    'partner_type': 'customer',
                })
                payment_type='receive_money'
            else:
                res.update({
                    'partner_type': 'supplier',
                })
                payment_type = 'send_money'
            # res.update({
            #     'payment_date':datetime.now().date()
            # })
            vals.append((0, 0, {
                'invoice_id': inv and inv.id or False,
                'partner_id': inv and inv.partner_id.id or False,
                'payment_amount': inv.amount_residual or 0.0,
                # 'paid_amount': inv.amount_residual or 0.0,
                'due_date':datetime.now().date() or False,
                'issue_date':datetime.now().date() or False,
                'payment_date':datetime.now().date() or False,
                'memo':inv.name or False,
                'payment_type':payment_type or False,

                # 'cheque_statement':None
            }))

        if inv_type in ('out_invoice', 'in_refund'):
            res.update({
                'payment_type': 'inbound'
            })
        else:
            res.update({
                'payment_type': 'outbound'
            })

        res.update({
            'invoice_ids': vals,
        })
        return res

    name = fields.Char('Name', default='hello')
    payment_type = fields.Selection(
        [('outbound', 'Send Money'), ('inbound', 'Receive Money'), ('transfer', 'Transfer')], string="Payment Type",
        required="1")
    payment_date = fields.Date('Payment Date',required=True)
    communication = fields.Char('Memo')
    partner_type = fields.Selection([('customer', 'Customer'), ('supplier', 'Supplier')], string='Partner Type')
    journal_id = fields.Many2one('account.journal', string='Payment Method',required=True,
                                 domain=[('type', '=', 'bank')])
    bank_id = fields.Many2one('res.bank', string="Branch")
    # invoice_ids = fields.One2many('pdc.wizard', 'bulk_pdc_invoice_id', string='Invoice')
    invoice_ids = fields.One2many('bulk.pdc.payment.line', 'bulk_pdc_invoice_id', string='Invoice')
    cheque_no = fields.Char('Cheque No')
    cheque_date = fields.Char('Cheque Date')

    # @api.onchange('payment_date')
    # def _set_line_payment_date(self):
    #     for rec in self.invoice_ids:
    #         rec.payment_date=self.payment_date
    @api.onchange('journal_id')
    def _set_journal(self):
        for rec in self:
            for line in rec.invoice_ids:
                line.journal_id=rec.journal_id

    @api.onchange('bank_id')
    def _set_bank(self):
        for rec in self:
            for line in rec.invoice_ids:
                line.bank_id=rec.bank_id

    def process_payment(self):
        line_length=len(self.invoice_ids)
        count=0
        for line in self.invoice_ids:
            if line.journal_id:
                count=count+1
        if line_length==count:
            for line in self.invoice_ids:
                vals={
                    'payment_type':line.payment_type,
                    'partner_id':line.partner_id.id,
                    'payment_amount':line.payment_amount,
                    'company_id':self.env.company.id,
                    'currency_id':self.env.company.currency_id.id,
                    'reference':line.reference,
                    'journal_id':line.journal_id.id,
                    'cheque_status':'paid',
                    'payment_date':line.payment_date,
                    'due_date':line.due_date,
                    'issue_date':line.issue_date,
                    'memo':line.memo,
                    'agent':line.agent,
                    'bank_id':line.bank_id.id,
                    'invoice_id':line.invoice_id.id,
                    'state':'draft',
                    'attachment_ids':[(6,0,line.attachment_ids.ids)],
                }
                sh_pdc=self.env['pdc.wizard'].sudo().create(vals)
                sh_pdc.button_register()
                # sh_pdc.action_register()
                # sh_pdc.action_deposited()
                # sh_pdc.action_done()
                # for pdc in sh_pdc:
                #     pdc.deposited_debit.partner_id=pdc.partner_id.id
                #     pdc.deposited_credit.partner_id=pdc.partner_id.id
                #
                #     for inv in pdc.invoice_id:
                #         for lines in inv.line_ids:
                #             if lines.account_id.id ==pdc.deposited_debit.account_id.id:
                #                 for pdc_journal in pdc.deposited_debit.move_id:
                #                     lines += pdc_journal.line_ids.filtered(lambda
                #                                                               line: line.account_id.id ==pdc.deposited_debit.account_id.id and not line.reconciled)
                #
                #                     lines.reconcile()
                #
                #             if lines.account_id.id == pdc.deposited_credit.account_id.id:
                #                 for pdc_journal in pdc.deposited_debit.move_id:
                #                     lines += pdc_journal.line_ids.filtered(lambda
                #                                                                line: line.account_id.id == pdc.deposited_credit.account_id.id and not line.reconciled)
                #                     lines.reconcile()


        else:
            for line in self.invoice_ids:
                if not line.journal_id:
                    raise ValidationError(_("Payment journal mandatory for :"+line.invoice_id))

        return True


class bulk_pdc_inv_payment_line(models.TransientModel):
    _name = "bulk.pdc.payment.line"

    bulk_pdc_invoice_id = fields.Many2one('bulk.pdc.payment')
    name = fields.Char("Name", default='New', readonly=1)
    # check_amount_in_words = fields.Char(string="Amount in Words", compute='_compute_check_amount_in_words')
    invoice_id = fields.Many2one('account.move', string="Invoice/Bill")
    partner_id = fields.Many2one('res.partner', string="Partner", required=True)
    payment_amount = fields.Float("Payment Amount")
    issue_date = fields.Date("Issue Date", required=1, default=fields.Date.today())
    payment_date = fields.Date("Payment/Due Date", default=fields.Date.today(), required=1)
    memo = fields.Char("Memo")
    payment_type = fields.Selection([('receive_money', 'Receive Money'), ('send_money', 'Send Money')],required=1,
                                    string="Payment Type",)
    attachment_ids = fields.Many2many('ir.attachment', string='Cheque Image')
    currency_id = fields.Many2one('res.currency', string="Currency", default=lambda self: self.env.company.currency_id)
    reference = fields.Char("Cheque No")
    journal_id = fields.Many2one('account.journal', string="Payment Journal", domain=[('type', '=', 'bank')])
    company_id = fields.Many2one('res.company', string='company', default=lambda self: self.env.company)
    cheque_status = fields.Selection([('draft','Draft'),('deposit','Deposit'),('paid','Paid')],string="Cheque Status",default='paid')
    due_date = fields.Date("Due Date", required=1, default=fields.Date.today())
    agent = fields.Char("Agent")
    bank_id = fields.Many2one('res.bank', string="Branch")
















