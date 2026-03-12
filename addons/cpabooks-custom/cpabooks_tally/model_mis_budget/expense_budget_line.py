from odoo import models, fields, api, _

class ExpenseMisBudgetLine(models.Model):
    _name = 'expense.mis.budget.line'
    _description = 'Expense MIS Budget Line'

    mis_id = fields.Many2one('mis.budget', 'MIS Budget')

    # Actual CY
    actual_cy_account = fields.Many2one('account.account', 'Actual CY')
    actual_cy_jan = fields.Float('JAN')
    actual_cy_feb = fields.Float('FEB')
    actual_cy_mar = fields.Float('MAR')
    actual_cy_apr = fields.Float('APR')
    actual_cy_may = fields.Float('MAY')
    actual_cy_jun = fields.Float('JUN')
    actual_cy_jul = fields.Float('JUL')
    actual_cy_aug = fields.Float('AUG')
    actual_cy_sep = fields.Float('SEP')
    actual_cy_oct = fields.Float('OCT')
    actual_cy_nov = fields.Float('NOV')
    actual_cy_dec = fields.Float('DEC')
    actual_cy_total = fields.Float('Total', compute='_compute_totals')

    # Actual LY (Computed Field)
    actual_ly_account_id = fields.Many2one('account.account', 'Actual LY', readonly=True, compute='_set_accounts')
    actual_ly_jan = fields.Float('JAN')
    actual_ly_feb = fields.Float('FEB')
    actual_ly_mar = fields.Float('MAR')
    actual_ly_apr = fields.Float('APR')
    actual_ly_may = fields.Float('MAY')
    actual_ly_jun = fields.Float('JUN')
    actual_ly_jul = fields.Float('JUL')
    actual_ly_aug = fields.Float('AUG')
    actual_ly_sep = fields.Float('SEP')
    actual_ly_oct = fields.Float('OCT')
    actual_ly_nov = fields.Float('NOV')
    actual_ly_dec = fields.Float('DEC')
    actual_ly_total = fields.Float('Total', compute='_compute_totals')

    # Payment CYP (Computed Field)
    payment_cyp_account = fields.Many2one('account.account', 'Payment CYP', readonly=True, compute='_set_accounts')
    payment_cyp_jan = fields.Float('JAN')
    payment_cyp_feb = fields.Float('FEB')
    payment_cyp_mar = fields.Float('MAR')
    payment_cyp_apr = fields.Float('APR')
    payment_cyp_may = fields.Float('MAY')
    payment_cyp_jun = fields.Float('JUN')
    payment_cyp_jul = fields.Float('JUL')
    payment_cyp_aug = fields.Float('AUG')
    payment_cyp_sep = fields.Float('SEP')
    payment_cyp_oct = fields.Float('OCT')
    payment_cyp_nov = fields.Float('NOV')
    payment_cyp_dec = fields.Float('DEC')
    payment_cyp_total = fields.Float('Total', compute='_compute_totals')

    # Budget CY (Computed Field)
    budget_cy_account = fields.Many2one('account.account', 'Budget CY', readonly=True, compute='_set_accounts')
    budget_cy_jan = fields.Float('JAN')
    budget_cy_feb = fields.Float('FEB')
    budget_cy_mar = fields.Float('MAR')
    budget_cy_apr = fields.Float('APR')
    budget_cy_may = fields.Float('MAY')
    budget_cy_jun = fields.Float('JUN')
    budget_cy_jul = fields.Float('JUL')
    budget_cy_aug = fields.Float('AUG')
    budget_cy_sep = fields.Float('SEP')
    budget_cy_oct = fields.Float('OCT')
    budget_cy_nov = fields.Float('NOV')
    budget_cy_dec = fields.Float('DEC')
    budget_cy_total = fields.Float('Total', compute='_compute_totals')

    # Budget LY (Computed Field)
    budget_ly_account = fields.Many2one('account.account', 'Budget LY', readonly=True, compute='_set_accounts')
    budget_ly_jan = fields.Float('JAN')
    budget_ly_feb = fields.Float('FEB')
    budget_ly_mar = fields.Float('MAR')
    budget_ly_apr = fields.Float('APR')
    budget_ly_may = fields.Float('MAY')
    budget_ly_jun = fields.Float('JUN')
    budget_ly_jul = fields.Float('JUL')
    budget_ly_aug = fields.Float('AUG')
    budget_ly_sep = fields.Float('SEP')
    budget_ly_oct = fields.Float('OCT')
    budget_ly_nov = fields.Float('NOV')
    budget_ly_dec = fields.Float('DEC')
    budget_ly_total = fields.Float('Total', compute='_compute_totals')

    @api.depends('actual_cy_account')
    def _set_accounts(self):
        for rec in self:
            account_id = rec.actual_cy_account.id if rec.actual_cy_account else False
            rec.actual_ly_account_id = account_id
            rec.payment_cyp_account = account_id
            rec.budget_ly_account = account_id
            rec.budget_cy_account = account_id

    @api.depends('actual_cy_jan', 'actual_cy_feb', 'actual_cy_mar', 'actual_cy_apr', 'actual_cy_may', 'actual_cy_jun', 'actual_cy_jul', 'actual_cy_aug', 'actual_cy_sep', 'actual_cy_oct', 'actual_cy_nov', 'actual_cy_dec',
                 'actual_ly_jan', 'actual_ly_feb', 'actual_ly_mar', 'actual_ly_apr', 'actual_ly_may', 'actual_ly_jun', 'actual_ly_jul', 'actual_ly_aug', 'actual_ly_sep', 'actual_ly_oct', 'actual_ly_nov', 'actual_ly_dec',
                 'payment_cyp_jan', 'payment_cyp_feb', 'payment_cyp_mar', 'payment_cyp_apr', 'payment_cyp_may', 'payment_cyp_jun', 'payment_cyp_jul', 'payment_cyp_aug', 'payment_cyp_sep', 'payment_cyp_oct', 'payment_cyp_nov', 'payment_cyp_dec',
                 'budget_cy_jan', 'budget_cy_feb', 'budget_cy_mar', 'budget_cy_apr', 'budget_cy_may', 'budget_cy_jun', 'budget_cy_jul', 'budget_cy_aug', 'budget_cy_sep', 'budget_cy_oct', 'budget_cy_nov', 'budget_cy_dec',
                 'budget_ly_jan', 'budget_ly_feb', 'budget_ly_mar', 'budget_ly_apr', 'budget_ly_may', 'budget_ly_jun', 'budget_ly_jul', 'budget_ly_aug', 'budget_ly_sep', 'budget_ly_oct', 'budget_ly_nov', 'budget_ly_dec')
    def _compute_totals(self):
        for rec in self:
            rec.actual_cy_total = sum([getattr(rec, f'actual_cy_{m}') for m in ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec']])
            rec.actual_ly_total = sum([getattr(rec, f'actual_ly_{m}') for m in ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec']])
            rec.payment_cyp_total = sum([getattr(rec, f'payment_cyp_{m}') for m in ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec']])
            rec.budget_cy_total = sum([getattr(rec, f'budget_cy_{m}') for m in ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec']])
            rec.budget_ly_total = sum([getattr(rec, f'budget_ly_{m}') for m in ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec']])
