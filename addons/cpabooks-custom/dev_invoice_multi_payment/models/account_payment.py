# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://www.devintellecs.com>).
#
#    For Module Support : devintelle@gmail.com  or Skype : devintelle 
#
##############################################################################

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class account_move_line(models.Model):
    _inherit='account.move.line'
    
    adv_payment_id = fields.Many2one('advance.payment.line', string='Multi Payment Id')

class account_move(models.Model):
    _inherit='account.move'
    
    inv_id = fields.Many2one('account.move', string='Invoice')

class account_payment(models.Model):
    _inherit = 'account.payment'

    payment_for = fields.Selection([
        ('on_account', 'On Account Payment'),
        ('multi_payment', 'Invoice Payment'),
        ('bank','Bank'),
        ('cash','Cash')
    ], string='Payment Method', default='on_account')
    adv_line_ids = fields.One2many('advance.payment.line', 'account_payment_id')
    full_reco = fields.Boolean('Full Reconcile')
    allocation_amount = fields.Float('Total Amount', compute='get_allocation_amount')
    woff_amount=fields.Monetary(string="Write-Off Amount",currency_field='currency_id')
    woff_label=fields.Char(string="Write-Off Label", default="Write-Off")
    woff_account=fields.Many2one('account.account',string="Write-Off Account")

    def action_launch_multi_payment(self):
        return {
                'name': 'Register Payment',
                'type': 'ir.actions.act_window',
                'res_model': 'bulk.inv.payment',
                'view_mode': 'form',
                'target': 'new',
        }

    @api.onchange('woff_label','woff_account')
    def set_label_and_account(self):
        for rec in self:
            if rec.woff_amount > 0:
                for line in rec.adv_line_ids.filtered(lambda env: env.allocation > 0):
                    line.woff_label=rec.woff_label
                    line.woff_account=rec.woff_account.id
            if rec.woff_amount == 0:
                for line in rec.adv_line_ids:
                    line.woff_label=None
                    line.woff_account=None

    @api.onchange('woff_amount','woff_label','woff_account')
    def set_write_off(self):
        for rec in self:
            if rec.woff_amount>0:
                woff_amt=rec.woff_amount
                for line in rec.adv_line_ids.filtered(lambda env:env.allocation>0):
                    line.woff_amount=0
                for line in rec.adv_line_ids.filtered(lambda env:env.allocation>0):
                    if woff_amt>0:
                        if line.balance_amount-line.allocation>woff_amt:
                            line.woff_amount=woff_amt
                            line.diff_amt=line.balance_amount-(line.allocation+woff_amt)
                            woff_amt=0
                        else:
                            line.woff_amount=woff_amt-(line.balance_amount-line.allocation)
                            line.diff_amt=line.balance_amount-(line.allocation+(woff_amt-(line.balance_amount-line.allocation)))
                            woff_amt-=line.balance_amount-line.allocation
            if rec.woff_amount==0:
                for line in rec.adv_line_ids.filtered(lambda env:env.allocation>0):
                    line.diff_amt = line.balance_amount - line.allocation
                    line.woff_amount = 0


    
    @api.depends('adv_line_ids','adv_line_ids.allocation')
    def get_allocation_amount(self):
        for payment in self:
            amount = 0
            payment.allocation_amount = 0
            for line in payment.adv_line_ids:
                amount += line.allocation
            payment.allocation_amount = amount
            
    
    @api.onchange('payment_for')
    def onchange_payment_for(self):
        if self.payment_for != 'multi_payment':
            for line in self.adv_line_ids:
                line.unlink()

    @api.onchange('currency_id')
    def onchange_currency(self):
        curr_pool = self.env['res.currency']
        if self.currency_id and self.adv_line_ids:
            for line in self.adv_line_ids:
                if line.currency_id.id != self.currency_id.id:
                    currency_id = self.currency_id.with_context(date=self.date)
                    line.original_amount = curr_pool._compute(line.currency_id, currency_id, line.original_amount,
                                                              round=True)
                    line.balance_amount = curr_pool._compute(line.currency_id, currency_id, line.balance_amount,
                                                             round=True)
                    line.allocation = curr_pool._compute(line.currency_id, currency_id, line.allocation, round=True)
                    line.currency_id = self.currency_id and self.currency_id.id or False
        self.amount = 0.0
        
    def remove_lines(self):
        for line in self.adv_line_ids:
            if line.allocation <= 0:
                line.unlink()
    
    
    def _synchronize_from_moves(self, changed_fields):
        for payment in self:
            if payment.payment_for == 'multi_payment':
                return True
        return super(account_payment,self)._synchronize_from_moves(changed_fields)
    
    def dev_reconcile(self):
        for line in self.adv_line_ids:
            invoice_id = line.invoice_id
            move_line = self.env['account.move.line'].search([('move_id','=',self.move_id.id),('adv_payment_id','=',line.id)])
            invoice_id.js_assign_outstanding_line(move_line.id)
        return True
        
    def more_amount_payment_line(self,amount):
        if self.payment_type == 'inbound':
            counterpart_amount = -amount
        elif self.payment_type == 'outbound':
            counterpart_amount = amount
        else:
            counterpart_amount = 0.0
        
        balance = self.currency_id._convert(counterpart_amount, self.company_id.currency_id, self.company_id, self.date)
        counterpart_amount_currency = counterpart_amount
        currency_id = self.currency_id.id
        
        if self.is_internal_transfer:
            if self.payment_type == 'inbound':
                liquidity_line_name = _('Transfer to %s', self.journal_id.name)
            else: # payment.payment_type == 'outbound':
                liquidity_line_name = _('Transfer from %s', self.journal_id.name)
        else:
            liquidity_line_name = self.payment_reference

        # Compute a default label to set on the journal items.

        payment_display_name = {
            'outbound-customer': _("Customer Reimbursement"),
            'inbound-customer': _("Customer Payment"),
            'outbound-supplier': _("Vendor Payment"),
            'inbound-supplier': _("Vendor Reimbursement"),
        }

        default_line_name = self.env['account.move.line']._get_default_line_name(
            _("Internal Transfer") if self.is_internal_transfer else payment_display_name['%s-%s' % (self.payment_type, self.partner_type)],
            amount,
            self.currency_id,
            self.date,
            partner=self.partner_id,
        )
        new_lines  = []
        liq_dic = {
            'name': liquidity_line_name or default_line_name,
            'date_maturity': self.date,
            'amount_currency': -counterpart_amount_currency,
            'currency_id': currency_id,
            'debit': balance < 0.0 and -balance or 0.0,
            'credit': balance > 0.0 and balance or 0.0,
            'partner_id': self.partner_id.id,
            'account_id': self.journal_id.payment_debit_account_id.id if balance < 0.0 else self.journal_id.payment_credit_account_id.id,
        }
            # Receivable / Payable.
        rec_dict={
            'name': self.payment_reference or default_line_name,
            'date_maturity': self.date,
            'amount_currency': counterpart_amount_currency if currency_id else 0.0,
            'currency_id': currency_id,
            'debit': balance > 0.0 and balance or 0.0,
            'credit': balance < 0.0 and -balance or 0.0,
            'partner_id': self.partner_id.id,
            'account_id': self.destination_account_id.id,
        }
        new_lines.append(liq_dic)
        new_lines.append(rec_dict)
        return new_lines
        
    def check_multi_payment(self):
        pay_amt = "{:.2f}".format(self.amount)
        amt = "{:.2f}".format(self.allocation_amount)
        pay_amt = float(pay_amt)
        amt = float(amt)
        if not amt:
            raise ValidationError(("Add Allocation Amount in payment item"))

        if pay_amt < amt:
            raise ValidationError(("Amount is must be greater or equal '%s'") %(amt))
        return True

    # def action_draft(self):
    #     ''' posted -> draft '''
    #     self.move_id.button_draft()
    #     for pay in self.with_context(skip_account_move_synchronization=True):
    #         liquidity_lines, counterpart_lines, writeoff_lines = pay._seek_for_lines()
    #         if writeoff_lines:
    #             self.move_id.write({
    #                 'posted_before':False
    #             })
    #             self.move_id.unlink()



    def _synchronize_to_moves(self, changed_fields):
        for rec in self:
            if rec.woff_amount:
                if not any(field_name in changed_fields for field_name in (
                        'date', 'amount', 'payment_type', 'partner_type', 'payment_reference', 'is_internal_transfer',
                        'currency_id', 'partner_id', 'destination_account_id', 'partner_bank_id','woff_amount'
                )):
                    return
                for pay in self.with_context(skip_account_move_synchronization=True):
                    liquidity_lines, counterpart_lines, writeoff_lines = pay._seek_for_lines()

                    # Make sure to preserve the write-off amount.
                    # This allows to create a new payment with custom 'line_ids'.

                    if writeoff_lines:
                        writeoff_amount = sum(writeoff_lines.mapped('amount_currency'))
                        counterpart_amount = counterpart_lines['amount_currency']
                        if writeoff_amount > 0.0 and counterpart_amount > 0.0:
                            sign = 1
                        else:
                            sign = -1

                        write_off_line_vals = {
                            'name': writeoff_lines[0].name,
                            'amount': writeoff_amount * sign,
                            'account_id': writeoff_lines[0].account_id.id,
                        }
                    else:
                        if rec.woff_amount:
                            counterpart_woff_amount = 0.0
                            if self.payment_type == 'inbound':
                                counterpart_woff_amount = -rec.woff_amount
                            elif self.payment_type == 'outbound':
                                counterpart_woff_amount = rec.woff_amount
                            else:
                                counterpart_woff_amount = 0.0
                            write_off_line_vals = {
                                'name': rec.woff_label,
                                'date_maturity': self.date,
                                'amount_currency': -counterpart_woff_amount,
                                'currency_id': rec.currency_id.id,
                                'debit': counterpart_woff_amount < 0.0 and -counterpart_woff_amount or 0.0,
                                'credit': counterpart_woff_amount > 0.0 and counterpart_woff_amount or 0.0,
                                'partner_id': rec.partner_id.id,
                                'account_id': rec.woff_account.id,
                                'amount': rec.woff_amount,
                            }

                    line_vals_list = pay._prepare_move_line_default_vals(write_off_line_vals=write_off_line_vals)

                    line_ids_commands = [
                        (1, liquidity_lines.id, line_vals_list[0]),
                        (1, counterpart_lines.id, line_vals_list[1]),
                    ]

                    for line in writeoff_lines:
                        line_ids_commands.append((2, line.id))

                    if line_vals_list[2]:
                        line_ids_commands.append((0, 0, line_vals_list[2]))

                    # Update the existing journal items.
                    # If dealing with multiple write-off lines, they are dropped and a new one is generated.

                    pay.move_id.write({
                        'partner_id': pay.partner_id.id,
                        'currency_id': pay.currency_id.id,
                        'partner_bank_id': pay.partner_bank_id.id,
                        'line_ids': line_ids_commands,
                    })
            else:
                for pay in self.with_context(skip_account_move_synchronization=True):
                    liquidity_lines, counterpart_lines, writeoff_lines = pay._seek_for_lines()
                    if writeoff_lines:
                        if rec.payment_type=='inbound':
                            debit=writeoff_lines.debit+liquidity_lines.debit
                            rec.move_id.write({
                                'line_ids': [(1, liquidity_lines.id,{'debit':debit}),(1,writeoff_lines.id,{'debit':0})]
                            })
                        if rec.payment_type=='inbound':
                            credit=writeoff_lines.credit+liquidity_lines.credit
                            rec.move_id.write({
                                'line_ids': [(1, liquidity_lines.id, {'credit': credit}),(1,writeoff_lines.id,{'debit':0})]
                            })
                return super(account_payment, self)._synchronize_to_moves(changed_fields)
        
    def _prepare_move_line_default_vals(self, write_off_line_vals=None):
        for rec in self:
            if rec.woff_amount:
                counterpart_woff_amount=0.0
                if self.payment_type == 'inbound':
                    counterpart_woff_amount = -rec.woff_amount
                elif self.payment_type == 'outbound':
                    counterpart_woff_amount = rec.woff_amount
                else:
                    counterpart_woff_amount = 0.0
                write_off_line_vals={
                        'name': rec.woff_label,
                        'date_maturity': self.date,
                        'amount_currency': -counterpart_woff_amount,
                        'currency_id': rec.currency_id.id,
                        'debit': counterpart_woff_amount < 0.0 and -counterpart_woff_amount or 0.0,
                        'credit': counterpart_woff_amount > 0.0 and counterpart_woff_amount or 0.0,
                        'partner_id': rec.partner_id.id,
                        'account_id': rec.woff_account.id,
                        'amount':rec.woff_amount,
                    }
                return super(account_payment, self)._prepare_move_line_default_vals(write_off_line_vals)
            else:
                return super(account_payment, self)._prepare_move_line_default_vals(write_off_line_vals)

    def _remove_line(self):
        line_ids = self.adv_line_ids.filtered(lambda line: line.allocation == 0.0)
        line_ids.unlink()

    def dev_generate_moves(self):
        if self.payment_for == 'multi_payment':
            self.check_multi_payment()
            line_vals_list = []
            total_amount = self.amount
            for line in self.adv_line_ids.filtered(lambda env:env.allocation>0):
                total_amount = total_amount - line.allocation
                if self.payment_type == 'inbound':
                    counterpart_amount = -line.allocation
                    counterpart_woff_amount = -line.woff_amount
                    if line.invoice_id.move_type == 'out_refund':
                        counterpart_amount = line.allocation
                        counterpart_woff_amount = line.woff_amount
                elif self.payment_type == 'outbound':
                    counterpart_amount = line.allocation
                    counterpart_woff_amount = line.woff_amount
                    if line.invoice_id.move_type == 'in_refund':
                        counterpart_amount = -line.allocation
                        counterpart_woff_amount = -line.woff_amount
                else:
                    counterpart_amount = 0.0
                    counterpart_woff_amount = 0.0

                balance = self.currency_id._convert(counterpart_amount, self.company_id.currency_id, self.company_id, self.date)
                counterpart_amount_currency = counterpart_amount
                counterpart_woff_amount_currency = counterpart_woff_amount
                woff_balance=self.currency_id._convert(counterpart_woff_amount, self.company_id.currency_id, self.company_id, self.date)
                currency_id = self.currency_id.id

                if self.is_internal_transfer:
                    if self.payment_type == 'inbound':
                        liquidity_line_name = _('Transfer to %s', self.journal_id.name)
                    else: # payment.payment_type == 'outbound':
                        liquidity_line_name = _('Transfer from %s', self.journal_id.name)
                else:
                    liquidity_line_name = self.payment_reference

                # Compute a default label to set on the journal items.

                payment_display_name = {
                    'outbound-customer': _("Customer Reimbursement"),
                    'inbound-customer': _("Customer Payment"),
                    'outbound-supplier': _("Vendor Payment"),
                    'inbound-supplier': _("Vendor Reimbursement"),
                }

                default_line_name = self.env['account.move.line']._get_default_line_name(
                    _("Internal Transfer") if self.is_internal_transfer else payment_display_name['%s-%s' % (self.payment_type, self.partner_type)],
                    line.allocation,
                    self.currency_id,
                    self.date,
                    partner=self.partner_id,
                )

                
                    # Liquidity line.
                liq_dic = {
                    'name': liquidity_line_name or default_line_name,
                    'date_maturity': self.date,
                    'amount_currency': -counterpart_amount_currency,
                    'currency_id': currency_id,
                    'debit': balance < 0.0 and -balance or 0.0,
                    'credit': balance > 0.0 and balance or 0.0,
                    'partner_id': self.partner_id.id,
                    'account_id': self.journal_id.payment_debit_account_id.id if balance < 0.0 else self.journal_id.payment_credit_account_id.id,
                }
                    # Receivable / Payable.
                if line.woff_amount>0 and line.allocation>0:
                    total_amount = total_amount - (line.allocation+line.woff_amount)
                    if balance>0.0:
                        balance+=line.woff_amount
                    else:
                        balance-=line.woff_amount
                    woff_dict = {
                        'name': line.woff_label,
                        'date_maturity': self.date,
                        'amount_currency': -counterpart_woff_amount_currency,
                        'currency_id': currency_id,
                        'debit': woff_balance < 0.0 and -woff_balance or 0.0,
                        'credit': woff_balance > 0.0 and woff_balance or 0.0,
                        'partner_id': self.partner_id.id,
                        'account_id': line.woff_account.id,
                    }
                    line_vals_list.append(woff_dict)
                rec_dict={
                    'name': self.payment_reference or default_line_name,
                    'date_maturity': self.date,
                    'amount_currency': counterpart_amount_currency if currency_id else 0.0,
                    'currency_id': currency_id,
                    'debit': balance > 0.0 and balance or 0.0,
                    'credit': balance < 0.0 and -balance or 0.0,
                    'partner_id': self.partner_id.id,
                    'account_id': self.destination_account_id.id,
                    'adv_payment_id':line.id,
                }

                line_vals_list.append(liq_dic)
                line_vals_list.append(rec_dict)

            if total_amount > 0:
                n_lines = self.more_amount_payment_line(total_amount)
                for n_l in n_lines:
                    line_vals_list.append(n_l)
                    
            self.move_id.line_ids.unlink()
            self.move_id.line_ids = [(0, 0, line_vals) for line_vals in line_vals_list]
            self.move_id.action_post()
            for line in self.adv_line_ids.filtered(lambda env:env.allocation>0):
                invoice_id = line.invoice_id
                move_line = self.env['account.move.line'].search([('move_id','=',self.move_id.id),('adv_payment_id','=',line.id)])
                invoice_id.js_assign_outstanding_line(move_line.id)
            self._remove_line()
            return True
        
    
    def load_payment_lines(self):
        if self.payment_for == 'multi_payment':
            self.adv_line_ids.unlink()
            account_inv_obj = self.env['account.move']
            invoice_ids=[]
            partner_ids = self.env['res.partner'].search([('parent_id','=',self.partner_id.id)]).ids
            partner_ids.append(self.partner_id.id)
            query = """ select id from account_move where partner_id in %s and state = %s and move_type in %s and company_id = %s and payment_state != %s and amount_residual != 0"""
            if self.partner_type == 'customer':
                params = (tuple(partner_ids),'posted',('out_invoice','out_refund'), self.company_id.id, 'paid')
            else:
                params = (tuple(partner_ids),'posted',('in_invoice','in_refund'), self.company_id.id, 'paid')
            self.env.cr.execute(query, params)
            result = self.env.cr.dictfetchall()
            invoice_ids = [inv.get('id') for inv in result]
            invoice_ids = account_inv_obj.browse(invoice_ids)
            curr_pool = self.env['res.currency']
            for vals in invoice_ids:
                account_id = False
                if self.partner_type == 'customer':
                    account_id = vals.partner_id and vals.partner_id.property_account_receivable_id.id or False
                else:
                    account_id = vals.partner_id and vals.partner_id.property_account_payable_id.id or False
                    
                original_amount = vals.amount_total
                balance_amount = vals.amount_residual
                allocation = vals.amount_residual
                if vals.currency_id.id != self.currency_id.id:
                    original_amount = vals.amount_total
                    balance_amount = vals.amount_residual
                    allocation = vals.amount_residual
                    if vals.currency_id.id != self.currency_id.id:
                        currency_id = self.currency_id.with_context(date=self.date)
                        original_amount = curr_pool._compute(vals.currency_id, currency_id, original_amount, round=True)
                        balance_amount = curr_pool._compute(vals.currency_id, currency_id, balance_amount, round=True)
                        allocation = curr_pool._compute(vals.currency_id, currency_id, allocation, round=True)

                query = """ INSERT INTO advance_payment_line (invoice_id, account_id, date, due_date, original_amount, balance_amount, currency_id, account_payment_id) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)"""
                params = (vals.id,account_id, vals.invoice_date, vals.invoice_date_due, original_amount, balance_amount, self.currency_id.id, self.id)
                self.env.cr.execute(query, params)
            
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
