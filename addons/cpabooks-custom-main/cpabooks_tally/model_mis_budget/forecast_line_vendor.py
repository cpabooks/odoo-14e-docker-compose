from odoo import api, models, fields, _


class ForecastLineVendor(models.Model):
    """Forecast line for vendors"""
    _name = 'forecast.line.vendor'
    _description = 'Forecast Line Vendor'

    @api.depends('partner_id', 'mis_id')
    def _get_opening(self):
        for rec in self:
            if rec.partner_id and rec.mis_id:
                budget_customer_id = self.env['budget.vendor.line'].search([
                    ('mis_id', '=', rec.mis_id.id),
                    ('actual_cy_partner', '=', rec.partner_id.id)
                ], limit=1)
                rec.opening = budget_customer_id.opening if budget_customer_id else 0.0

    mis_id = fields.Many2one('mis.budget')

    partner_id = fields.Many2one('res.partner', 'Vendor', domain=[('supplier_rand', '>=', 1)])
    opening = fields.Float('Opening', compute=_get_opening)
    cy = fields.Float('CY')
    cyp = fields.Float('CYP')
    receipt = fields.Float('Variance', compute="_compute_receipt")

    @api.depends('cy', 'cyp')
    def _compute_receipt(self):
        for rec in self:
            rec.receipt = rec.cy - rec.cyp