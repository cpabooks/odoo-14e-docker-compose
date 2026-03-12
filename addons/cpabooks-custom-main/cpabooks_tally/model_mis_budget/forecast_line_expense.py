from odoo import api, models, fields, _


class ForecastLineExpense(models.Model):
    _name = 'forecast.line.expense'
    _description = 'Expense Forecast Line'

    mis_id = fields.Many2one('mis.budget', 'MIS')

    #Expenses
    expense_account_id = fields.Many2one('account.account', 'Expense')
    expense_opening = fields.Float('Opening')
    expense_cy = fields.Float('CY')
    expense_cyp = fields.Float('CYP')
    expense_receipt = fields.Float('Variance', compute="_compute_receipt")

    @api.depends('expense_cy', 'expense_cyp')
    def _compute_receipt(self):
        for rec in self:
            rec.expense_receipt = rec.expense_cy - rec.expense_cyp