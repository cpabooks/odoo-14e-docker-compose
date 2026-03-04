from odoo import fields, models, api


class AccountPaymentInherit(models.TransientModel):
    _inherit = "account.payment.register"

    cheque_no=fields.Char(string="Cheque or Ref No.")
    cheque_date=fields.Date(string="Cheque Deposit Date")
    # is_chq_no_hide=fields.Boolean(default=False)
    custom_partial_amount=fields.Monetary()

    @api.model
    def _get_wizard_values_from_batch(self, batch_result):
        ''' Extract values from the batch passed as parameter (see '_get_batches')
        to be mounted in the wizard view.
        :param batch_result:    A batch returned by '_get_batches'.
        :return:                A dictionary containing valid fields
        '''
        key_values = batch_result['key_values']
        lines = batch_result['lines']
        company = lines[0].company_id


        source_amount = abs(sum(lines.mapped('amount_residual')))
        if source_amount==0:
            source_amount = abs(sum(lines.move_id.mapped('amount_residual')))
        if key_values['currency_id'] == company.currency_id.id:
            source_amount_currency = source_amount
        else:
            source_amount_currency = abs(sum(lines.mapped('amount_residual_currency')))
            if source_amount_currency==0:
                source_amount_currency = abs(sum(lines.move_id.mapped('amount_residual')))

        return {
            'company_id': company.id,
            'partner_id': key_values['partner_id'],
            'partner_type': key_values['partner_type'],
            'payment_type': key_values['payment_type'],
            'source_currency_id': key_values['currency_id'],
            'source_amount': source_amount,
            'source_amount_currency': source_amount_currency,
        }

    # @api.onchange('journal_id')
    # def _hide_cheque_no_field(self):
    #     for rec in self:
    #         if rec.journal_id.type=='cash':
    #             rec.is_chq_no_hide=True
    #         else:
    #             rec.is_chq_no_hide = False

    @api.onchange('amount')
    def _assign_in_custom_partial_amount(self):
        for rec in self:
            rec.custom_partial_amount=rec.amount


    @api.depends('source_amount', 'source_amount_currency', 'source_currency_id', 'company_id', 'currency_id',
                 'payment_date')
    def _compute_amount(self):
        for wizard in self:
            if wizard.custom_partial_amount > 0:
                wizard.amount = wizard.custom_partial_amount
            elif wizard.source_currency_id == wizard.currency_id:
                # Same currency.
                wizard.amount = wizard.source_amount_currency
            elif wizard.currency_id == wizard.company_id.currency_id:
                # Payment expressed on the company's currency.
                wizard.amount = wizard.source_amount
            else:
                # Foreign currency on payment different than the one set on the journal entries.
                amount_payment_currency = wizard.company_id.currency_id._convert(wizard.source_amount,
                                                                                 wizard.currency_id, wizard.company_id,
                                                                                 wizard.payment_date)
                wizard.amount = amount_payment_currency

    def _create_payment_vals_from_wizard(self):
        payment_vals = {
            'date': self.payment_date,
            'amount': self.amount,
            'payment_type': self.payment_type,
            'partner_type': self.partner_type,
            'ref': self.communication,
            'journal_id': self.journal_id.id,
            'currency_id': self.currency_id.id,
            'partner_id': self.partner_id.id,
            'partner_bank_id': self.partner_bank_id.id,
            'payment_method_id': self.payment_method_id.id,
            'destination_account_id': self.line_ids[0].account_id.id,
            'cheque_no':self.cheque_no,
            'cheque_date':self.cheque_date
        }

        if not self.currency_id.is_zero(self.payment_difference) and self.payment_difference_handling == 'reconcile':
            payment_vals['write_off_line_vals'] = {
                'name': self.writeoff_label,
                'amount': self.payment_difference,
                'account_id': self.writeoff_account_id.id,
            }
        return payment_vals

class AccountPaymentInherit(models.Model):
    _inherit = "account.payment"

    cheque_no = fields.Char(string="Cheque or Ref No.")
    cheque_date = fields.Date(string="Cheque Deposit Date")

    num_word = fields.Char(string="Payment In Word: ", compute='_compute_amount_in_word')

    @api.depends('amount')
    def _compute_amount_in_word(self):
        for order in self:
            order.num_word = ''
            if order.currency_id:
                order.num_word = str(order.currency_id.amount_to_text(order.amount))


