from odoo import api, models, fields, _


class ForecastLineIncome(models.Model):
    """Income and expenses Forecast"""
    _name = 'forecast.line.income'
    _description = 'Income Forecast Line'

    mis_id = fields.Many2one('mis.budget', 'MIS')
    #Income
    income_account_id = fields.Many2one('account.account', 'Income')
    income_opening = fields.Float('Opening')
    income_cy = fields.Float('CY')
    income_cyp = fields.Float('CYP')
    income_receipt = fields.Float('Variance', compute='_compute_receipt', store=True)


    @api.depends('income_cy', 'income_cyp')
    def _compute_receipt(self):
        for rec in self:
            rec.income_receipt = rec.income_cy - rec.income_cyp

