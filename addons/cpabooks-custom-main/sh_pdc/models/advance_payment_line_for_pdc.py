from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class advance_payment_line_pdc(models.Model):
    _name = 'advance.payment.line.pdc'
    _description = 'Advance Payment Line PDV'

    invoice_id = fields.Many2one('account.move', string='Invoice')
    account_id = fields.Many2one('account.account', string="Account")
    date = fields.Date(string="Date")
    due_date = fields.Date(string="Due Date")
    original_amount = fields.Float(string="Original Amount")
    balance_amount = fields.Float(string="Balance Amount")
    full_reconclle = fields.Boolean(string="Full Reconclle")
    allocation = fields.Float(string="Allocation")
    pdc_payment_id = fields.Many2one('pdc.wizard')
    diff_amt = fields.Float('Remaining Amount', compute='get_diff_amount', )
    currency_id = fields.Many2one('res.currency', string='Currency')
    woff_label = fields.Char(string="Label")
    woff_account = fields.Many2one("account.account", string="Write-Off Account")
    woff_amount = fields.Float(string="Write-Off Amount")

    @api.onchange('woff_amount')
    def set_woff_amount(self):
        for rec in self:
            # get_all_allocation_line_woff = sum(rec.pdc_payment_id.adv_line_ids.filtered(
            #     lambda env: env.woff_amount > 0 and env.id != rec.id).mapped('woff_amount'))
            # parent_woff_amount=rec.pdc_payment_id.woff_amount-get_all_allocation_line_woff
            if rec.allocation > 0:
                # if rec.woff_amount>0:
                #     if parent_woff_amount>rec.woff_amount:
                #         rec.diff_amt=0
                #     else:
                rec.diff_amt = rec.balance_amount - (rec.allocation + rec.woff_amount)
            if rec.allocation == 0:
                rec.diff_amt = rec.balance_amount
                rec.woff_amount = 0
                rec.woff_label = None
                rec.woff_account = None
            if rec.woff_amount > 0:
                rec.woff_label = rec.pdc_payment_id.woff_label
                rec.woff_account = rec.pdc_payment_id.woff_account.id

    @api.depends('balance_amount', 'allocation')
    def get_diff_amount(self):
        # for line in self:
        #     line.diff_amt = line.balance_amount - line.allocation
        for rec in self:
            # line.diff_amt = line.balance_amount - (line.allocation+line.woff_amount)
            get_all_allocation_line_woff=sum(rec.pdc_payment_id.adv_line_ids.filtered(lambda env:env.woff_amount>0 and env.id!=rec.id).mapped('woff_amount'))
            parent_woff_amount = rec.pdc_payment_id.woff_amount-get_all_allocation_line_woff
            if rec.allocation > 0:
                if parent_woff_amount > rec.balance_amount - rec.allocation:
                    rec.woff_amount = rec.balance_amount - rec.allocation
                    rec.diff_amt = 0
                else:
                    rec.woff_amount = parent_woff_amount
                    rec.diff_amt = rec.balance_amount - (rec.allocation + parent_woff_amount)
                if rec.woff_amount>0:
                    rec.woff_label = rec.pdc_payment_id.woff_label
                    rec.woff_account = rec.pdc_payment_id.woff_account.id
                else:
                    rec.woff_label = None
                    rec.woff_account = None
            if rec.allocation == 0:
                rec.woff_amount = 0
                rec.diff_amt = rec.balance_amount
                rec.woff_label = None
                rec.woff_account = None

    @api.onchange('full_reconclle')
    def onchange_full_reconclle(self):
        if self.full_reconclle:
            self.allocation = self.balance_amount

    @api.onchange('allocation')
    def onchange_allocation(self):
        if self.allocation:
            if self.allocation >= self.balance_amount:
                self.full_reconclle = True
            else:
                self.full_reconclle = False