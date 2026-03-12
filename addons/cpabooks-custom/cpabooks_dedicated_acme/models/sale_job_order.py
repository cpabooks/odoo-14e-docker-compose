from datetime import timedelta

from odoo import fields, models
from odoo.tools.safe_eval import datetime


class SaleJobOrder(models.Model):
    _name = 'sale.job.order'

    def _default_validity_date(self):
        if self.env['ir.config_parameter'].sudo().get_param('sale.use_quotation_validity_days'):
            days = self.env.company.quotation_validity_days
            if days > 0:
                return fields.Date.to_string(datetime.now() + timedelta(days))
        return False

    partner_id = fields.Many2one(
        'res.partner', string='Customer', readonly=True,
        states={'draft': [('readonly', False)], 'sent': [('readonly', False)]},
        required=True, change_default=True, index=True, tracking=1,
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]", )
    enquiry_number = fields.Char(string='Enquiry Number')
    attention = fields.Char(string='Attention')
    subject = fields.Char(string='Subject')
    delivery_details = fields.Char(string='Delivery')
    make = fields.Char(string='Make')
    bank_detail_enable = fields.Boolean(string='Bank Detail Enable')
    validity_date = fields.Date(string='Expiration', readonly=True, copy=False,
                                states={'draft': [('readonly', False)], 'sent': [('readonly', False)]},
                                default=_default_validity_date)
    date_order = fields.Datetime(string='Order Date', required=True, readonly=True, index=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}, copy=False, default=fields.Datetime.now)
    pricelist_id = fields.Many2one(
        'product.pricelist', string='Pricelist', check_company=True,
        required=True, readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]},
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]", tracking=1,
        help="If you change the pricelist, only newly added lines will be affected.")

    payment_term_id = fields.Many2one(
        'account.payment.term', string='Payment Terms', check_company=True,  # Unrequired company
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]", )
    discount_type=fields.Selection([('line','Order Line'),('global','Global')],string="")

