from odoo import api, models, fields, _


class BudgetVendorLine(models.Model):
    _name = 'budget.vendor.line'
    _description = 'Budget Vendor Line'

    @api.depends('actual_cy_partner')
    def _get_opening(self):
        for rec in self:
            if rec.actual_cy_partner:
                invoices = self.env['account.move'].search([
                    ('partner_id', '=', rec.actual_cy_partner.id),
                    ('move_type', '=', 'in_invoice')
                ])
                rec.opening = sum([inv.amount_residual for inv in invoices]) if invoices else 0.0

    mis_id = fields.Many2one('mis.budget', 'MIS Budget')

    # Computed Fields for Partner Names
    actual_cy_partner = fields.Many2one('res.partner', 'Actual CY', domain=[('supplier_rank', '>', 0)])
    actual_ly_partner_id = fields.Many2one('res.partner', 'Actual LY', domain=[('supplier_rank', '>', 0)], compute='_set_partner')
    payment_cyp_partner = fields.Many2one('res.partner', 'Payment CYP', domain=[('supplier_rank', '>', 0)], compute='_set_partner')
    budget_cy_partner = fields.Many2one('res.partner', 'Budget CY', domain=[('supplier_rank', '>', 0)], compute='_set_partner')
    budget_ly_partner = fields.Many2one('res.partner', 'Budget LY', domain=[('supplier_rank', '>', 0)], compute='_set_partner')
    opening = fields.Float('Opening', compute=_get_opening)

    # Actual CY
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

    # Actual LY
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

    # Payment CYP
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

    # Budget CY
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

    # Budget LY
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

    # Total Fields
    actual_cy_total = fields.Float('Actual CY Total', compute='_compute_totals', store=True)
    actual_ly_total = fields.Float('Actual LY Total', compute='_compute_totals', store=True)
    payment_cyp_total = fields.Float('Payment CYP Total', compute='_compute_totals', store=True)
    budget_cy_total = fields.Float('Budget CY Total', compute='_compute_totals', store=True)
    budget_ly_total = fields.Float('Budget LY Total', compute='_compute_totals', store=True)

    @api.depends('actual_cy_jan', 'actual_cy_feb', 'actual_cy_mar', 'actual_cy_apr', 'actual_cy_may', 'actual_cy_jun',
                 'actual_cy_jul', 'actual_cy_aug', 'actual_cy_sep', 'actual_cy_oct', 'actual_cy_nov', 'actual_cy_dec',
                 'actual_ly_jan', 'actual_ly_feb', 'actual_ly_mar', 'actual_ly_apr', 'actual_ly_may', 'actual_ly_jun',
                 'actual_ly_jul', 'actual_ly_aug', 'actual_ly_sep', 'actual_ly_oct', 'actual_ly_nov', 'actual_ly_dec',
                 'payment_cyp_jan', 'payment_cyp_feb', 'payment_cyp_mar', 'payment_cyp_apr', 'payment_cyp_may', 'payment_cyp_jun',
                 'payment_cyp_jul', 'payment_cyp_aug', 'payment_cyp_sep', 'payment_cyp_oct', 'payment_cyp_nov', 'payment_cyp_dec',
                 'budget_cy_jan', 'budget_cy_feb', 'budget_cy_mar', 'budget_cy_apr', 'budget_cy_may', 'budget_cy_jun',
                 'budget_cy_jul', 'budget_cy_aug', 'budget_cy_sep', 'budget_cy_oct', 'budget_cy_nov', 'budget_cy_dec',
                 'budget_ly_jan', 'budget_ly_feb', 'budget_ly_mar', 'budget_ly_apr', 'budget_ly_may', 'budget_ly_jun',
                 'budget_ly_jul', 'budget_ly_aug', 'budget_ly_sep', 'budget_ly_oct', 'budget_ly_nov', 'budget_ly_dec')
    def _compute_totals(self):
        for rec in self:
            rec.actual_cy_total = sum([
                rec.actual_cy_jan, rec.actual_cy_feb, rec.actual_cy_mar, rec.actual_cy_apr, rec.actual_cy_may, rec.actual_cy_jun,
                rec.actual_cy_jul, rec.actual_cy_aug, rec.actual_cy_sep, rec.actual_cy_oct, rec.actual_cy_nov, rec.actual_cy_dec
            ])
            rec.actual_ly_total = sum([
                rec.actual_ly_jan, rec.actual_ly_feb, rec.actual_ly_mar, rec.actual_ly_apr, rec.actual_ly_may, rec.actual_ly_jun,
                rec.actual_ly_jul, rec.actual_ly_aug, rec.actual_ly_sep, rec.actual_ly_oct, rec.actual_ly_nov, rec.actual_ly_dec
            ])
            rec.payment_cyp_total = sum([
                rec.payment_cyp_jan, rec.payment_cyp_feb, rec.payment_cyp_mar, rec.payment_cyp_apr, rec.payment_cyp_may, rec.payment_cyp_jun,
                rec.payment_cyp_jul, rec.payment_cyp_aug, rec.payment_cyp_sep, rec.payment_cyp_oct, rec.payment_cyp_nov, rec.payment_cyp_dec
            ])
            rec.budget_cy_total = sum([
                rec.budget_cy_jan, rec.budget_cy_feb, rec.budget_cy_mar, rec.budget_cy_apr, rec.budget_cy_may, rec.budget_cy_jun,
                rec.budget_cy_jul, rec.budget_cy_aug, rec.budget_cy_sep, rec.budget_cy_oct, rec.budget_cy_nov, rec.budget_cy_dec
            ])
            rec.budget_ly_total = sum([
                rec.budget_ly_jan, rec.budget_ly_feb, rec.budget_ly_mar, rec.budget_ly_apr, rec.budget_ly_may, rec.budget_ly_jun,
                rec.budget_ly_jul, rec.budget_ly_aug, rec.budget_ly_sep, rec.budget_ly_oct, rec.budget_ly_nov, rec.budget_ly_dec
            ])

    @api.depends('actual_cy_partner')
    def _set_partner(self):
        for rec in self:
            if rec.actual_cy_partner:
                rec.actual_ly_partner_id = rec.actual_cy_partner.id
                rec.payment_cyp_partner = rec.actual_cy_partner.id
                rec.budget_cy_partner = rec.actual_cy_partner.id
                rec.budget_ly_partner = rec.actual_cy_partner.id