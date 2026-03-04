from odoo import api, models, fields, _
from datetime import  date as date
import os


class AccountMove(models.Model):
    _inherit = 'account.move'

    payment_type_journal_id = fields.Many2one('account.journal','Payment Type',
                                              domain=lambda self: [('company_id','=', self.env.company.id),
                                                                   ('type', 'in', ['bank', 'cash'])])


    # @api.onchange('payment_type_journal_id')
    # def get_invoice_payment_term_id(self):
    #     for rec in self:
    #         if rec.payment_type_journal_id:
    #             immediate_payment = self.env['account.payment.term'].search([('name', '=', 'Immediate Payment')])
    #             rec.invoice_payment_term_id = immediate_payment.id

    # def action_post(self):
    #     res = super(AccountMove, self).action_post()
    #
    #     immediate_payment = self.env['account.payment.term'].search([('name', '=', 'Immediate Payment')])
    #     if res.state == 'posted' and res.invoice_payment_term_id == immediate_payment:
    #         return {
    #             'name': _('Register Payment'),
    #             'res_model': 'account.payment.register',
    #             'view_mode': 'form',
    #             'context': {
    #                 'active_model': 'account.move',
    #                 'active_ids': res.ids,
    #                 'payment_type': res.payment_type_journal_id.id,
    #                 'inv_name': res.name,
    #             },
    #             'target': 'new',
    #             'type': 'ir.actions.act_window',
    #         }
    #     return res

    # def action_trigger_payment_wizard(self):
    #     """This method can be called from a button in the form view."""
    #     if self.payment_register_required:
    #         return self.return_action_register_payment_wizard()
    #
    #
    # def action_register_payment(self):
    #     # Call the original method and get the result
    #     res = super(AccountMove, self).action_register_payment()
    #     for rec in self:
    #
    #         if 'context' in res:
    #             res['context'].update({
    #                 'inv_name': rec.name,
    #                 'inv_date': rec.invoice_date
    #             })
    #         else:
    #             res['context'] = {'inv_name': rec.name}
    #             res['context'] = {'inv_date': rec.invoice_date}
    #     return super(AccountMove, self).action_register_payment()


class AccountRegisterPayment(models.TransientModel):
    _inherit = 'account.payment.register'


    @api.onchange('is_invoice_date')
    def set_invoice_date(self):
        print(f'context {self.env.context}')
        inv_date = self.env.context.get('inv_date')
        for rec in self:
            if rec.is_invoice_date:
                rec.payment_date = inv_date
            else:
                rec.payment_date = date.today()



    clint_bank = fields.Char('Clint Bank Name')
    is_invoice_date = fields.Boolean('Invoice Date')
    narration = fields.Text('Narration')

    def action_create_payments(self):
        print(self)
        return super(AccountRegisterPayment, self).action_create_payments()
        for rec in self:
            if rec.narration:
                context = dict(self.env.context)  # Create a mutable copy of the context
                context.update({'narration': rec.narration})
                self = self.with_context(context)  # Reassign `self` with the updated context
            print(self.env.context)
        return super(AccountRegisterPayment, self).action_create_payments()

    @api.model
    def default_get(self, fields_list):
        """Get default values for the model by supering this method"""
        res = super(AccountRegisterPayment, self).default_get(fields_list)
        active_ids = self.env.context.get('active_ids')
        if active_ids:
            account_move_names = self.env['account.move'].browse(active_ids).mapped('name')
            res['communication'] = ', '.join(account_move_names)

        return res


    def _create_payment_vals_from_wizard(self):
        res = super(AccountRegisterPayment, self)._create_payment_vals_from_wizard()
        res['clint_bank'] = self.clint_bank
        print(f'res - {res}')
        return  res


