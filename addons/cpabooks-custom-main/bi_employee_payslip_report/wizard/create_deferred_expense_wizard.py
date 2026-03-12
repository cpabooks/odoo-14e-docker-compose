from odoo import api, models, fields, _
import datetime


class CreateDeferredExpenseWizard(models.TransientModel):
    _name = 'create.deferred.expense.wizard'
    _description = 'Create Deferred Expense Wizard'
    _rec_name = 'name'

    name = fields.Char('Name', default='NEW', readonly=True)
    start_date = fields.Date('Start Date', default=datetime.date.today(), required=True)
    end_date = fields.Date('End Date', required=True)

    @api.model
    def create(self, vals):
        res = super(CreateDeferredExpenseWizard, self).create(vals)

        res.write({
            'name': self.env['ir.sequence'].next_by_code('create.deferred.expense.wizard')
        })
        return res

    def action_create_deferred_expense(self):
        start_date = fields.Date.from_string(self.start_date)
        end_date = fields.Date.from_string(self.end_date)

        start_month_year = start_date.strftime('%B %Y')
        end_month_year = end_date.strftime('%B %Y')

        months_diff = (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month) + 1
        if months_diff < 1:
            months_diff = 1
        journal_id = self.env['account.journal'].search([
            ('name', 'ilike', 'Miscellaneous Operations'),
            ('type', '=', 'general')
        ], limit=1)

        fields_lst = [
            'total_cash_salary',
            'visa_cost',
            'leave_salary',
            'gratuity', 'air_fare',
            'medical_insurance',
            'house_rent'
        ]

        all_me_journals = self.env['config.me.journal'].sudo().search([])
        ctc_formula_lines = self.env['ctc.report.formula'].search([],limit=1).mapped('ctc_line_ids')
        for field in fields_lst:
            config_me_journal = self.env['config.me.journal'].search([
                ('journal_for', '=', field),
            ], limit=1)
            print(f'me journal {config_me_journal.name}')
            field_total = sum(ctc_formula_lines.mapped(field))
            original_value = field_total * months_diff

            print(f'{field} {original_value}')

            if config_me_journal in all_me_journals:
                journal_label = dict(self.env['config.me.journal'].fields_get(allfields=['journal_for'])['journal_for']['selection'])[field]

                name = f"{journal_label} Expenses for {start_month_year} - {end_month_year}"
                values = {
                    'asset_type': 'expense',
                    'name': name,
                    'first_depreciation_date': self.start_date,
                    'last_depreciation_date': self.end_date,
                    'method_number': months_diff,
                    'method_period': '1',
                    'prorata': False,
                    'original_value': original_value,
                    'account_depreciation_id': config_me_journal.deferred_expense_account_id.id,
                    'account_depreciation_expense_id': config_me_journal.expense_account_journal_id.id,
                    'journal_id': journal_id.id,
                    'company_id': self.env.company.id,
                }
                deffered_expenses = self.env['account.asset'].create(values)
                print(deffered_expenses.name)
