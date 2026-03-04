from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class AccountJournalInherit(models.Model):
    _inherit = "account.journal"

    @api.model
    def action_change_payment_debit_credit_id_method(self):
        get_all_journal = self.env['account.journal'].search([('type', 'in', ('bank', 'cash'))])
        for rec in get_all_journal:
            rec.payment_debit_account_id = rec.default_account_id
            rec.payment_credit_account_id = rec.default_account_id
            if 'default_credit_account_id' in self.env['account.journal']._fields:
                rec.default_credit_account_id = rec.default_account_id

    @api.onchange('default_account_id')
    def set_change_payment_debit_credit_id_method(self):
        for rec in self:
            rec.payment_debit_account_id = rec.default_account_id
            rec.payment_credit_account_id = rec.default_account_id
            if 'default_credit_account_id' in self.env['account.journal']._fields:
                rec.default_credit_account_id = rec.default_account_id

    @api.model
    def action_print(self):
        print('Updated cpabooks_accounting_automation')
    # Create journals from coa
    @api.model
    def create_journals_from_coa(self, *args, **kwargs):
        all_coas = self.env['account.account'].search([
            ('user_type_id.name', 'ilike', 'Bank and Cash'),
            '|',
            ('name', 'ilike', 'bank'),
            ('name', 'ilike', 'cash')
        ])

        for coa in all_coas:
            # Check if the account is already linked to a journal
            existing_journal = self.env['account.journal'].search([
                '|',
                ('default_account_id', '=', coa.id),
                ('payment_debit_account_id', '=', coa.id),
                ('payment_credit_account_id', '=', coa.id),
                ('company_id', '=', self.env.company.id)
            ], limit=1)

            name = coa.name
            words = name.split()
            code = ''.join((word[0] for word in words))



            journal_type = ''
            if 'bank' in coa.name.lower():
                journal_type = 'bank'
            elif 'cash' in coa.name.lower():
                journal_type = 'cash'

            if existing_journal:
                print(f"The account {coa.name} is already linked to the journal: {existing_journal.name}")
                existing_journal.write({
                    'name':coa.name,
                    'code':code
                })
                # raise ValidationError(_(f"The account {coa.name} is already linked to the journal: {existing_journal.name}"))
                continue

            # Create a new journal only if the account is not linked to another journal
            self.env['account.journal'].create({
                'name': coa.name,
                'type': journal_type,
                'default_account_id': coa.id,
                'code': code,
                'payment_debit_account_id': coa.id,
                'payment_credit_account_id': coa.id,
            })

# class AccountAccountInherit(models.Model):
#     _inherit = "account.account"
#
#
#     def write(self, vals):
#         res=super(AccountAccountInherit, self).write(vals)
#         for rec in self:
#             get_all_journal = self.env['account.journal'].search([('default_account_id', '=', rec.ids[0])])
#             for jour in get_all_journal:
#                 jour.payment_debit_account_id=rec
#                 jour.set_change_payment_debit_credit_id_method()


#
