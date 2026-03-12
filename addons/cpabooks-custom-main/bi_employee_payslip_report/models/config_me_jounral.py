from odoo import api, models, fields, _
import os
import csv


class ConfigMEJournals(models.Model):
    _name = 'config.me.journal'
    _description = 'Config ME Journals'
    _rec_name = 'name'

    name = fields.Char('Name', default='NEW', readonly=True)
    journal_for = fields.Selection([
        ('total_cash_salary', 'CTC-Cash'),
        ('leave_salary', 'Leave Salary'),
        ('gratuity', 'Gratuity'),
        ('air_fare', 'Air Fare'),
        ('medical_insurance', 'Medical Insurance'),
        ('visa_cost', 'Visa Cost'),
        ('house_rent', 'Camp/House Rent'),
    ], 'Journal For', required=True)
    deferred_expense_account_id = fields.Many2one('account.account', 'Deferred Expense Account')
    expense_account_journal_id = fields.Many2one('account.account', 'Expense Account Journal')
    company_id = fields.Many2one('res.company', 'Company')

    @api.model
    def default_get(self, fields_list):
        res = super(ConfigMEJournals, self).default_get(fields_list)
        res['company_id'] = self.env.company.id
        return res

    @api.model
    def create(self, vals):
        res = super(ConfigMEJournals, self).create(vals)
        if res.journal_for:
            journal_label = dict(self._fields['journal_for'].selection).get(res.journal_for)
            res.name = f'Journal Config for {journal_label}'
        return res

    def write(self, vals):
        res = super(ConfigMEJournals, self).write(vals)
        if vals.get('journal_for'):
            journal_label = dict(self._fields['journal_for'].selection).get(self.journal_for)
            self.name = f'Journal Config for {journal_label}'
        return res

    @api.model
    def action_create_me_journals(self, *args, **kwargs):
        csv_file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data', 'config.me.journal.csv'))
        # Open the CSV file
        with open(csv_file_path, mode='r', encoding='utf-8-sig') as csv_file:  # Use utf-8-sig to handle BOM
            csv_reader = csv.DictReader(csv_file)

            for row in csv_reader:
                journal_for = row['journal_for']
                deferred = row['deferred']
                expense = row['expense']

                # Search for deferred and expense accounts
                deferred_id = self.env['account.account'].search([
                    ('name', '=', deferred),
                    ('company_id', '=', self.env.company.id)
                ], limit=1, order="id asc")

                expense_id = self.env['account.account'].search([
                    ('name', '=', expense),
                    ('company_id', '=', self.env.company.id)
                ], limit=1, order="id asc")

                # Check if a journal with the same 'journal_for' already exists
                existing_journal = self.search([('journal_for', '=', journal_for)], limit=1)

                # Create a journal if it doesn't already exist
                if not existing_journal and journal_for and expense_id and deferred_id:
                    self.create({
                        'journal_for': journal_for,
                        'deferred_expense_account_id': deferred_id.id,
                        'expense_account_journal_id': expense_id.id
                    })
                    print(f'Created Journal for {journal_for}')
                elif existing_journal:
                    print(f'Skipped creation: Journal for {journal_for} already exists.')


