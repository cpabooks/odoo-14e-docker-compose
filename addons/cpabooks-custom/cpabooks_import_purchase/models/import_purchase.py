from datetime import datetime, time
from dateutil.relativedelta import relativedelta
from itertools import groupby
from pytz import timezone, UTC
from werkzeug.urls import url_encode

from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.osv import expression
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.float_utils import float_compare, float_is_zero
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tools.misc import formatLang, get_lang


class ImportPurchase(models.Model):
    _name = "import.purchase"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Import Purchase"
    # _order = 'priority desc, date_order desc, id desc'

    name = fields.Char('Import Reference', required=True, index=True, copy=False, default='New')
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True, default=lambda self: self.env.company.id)

    partner_id = fields.Many2one('res.partner', string='Vendor', required=True, change_default=True, tracking=True, domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]", help="You can find a vendor by its Name, TIN, Email or Internal Reference.")
    partner_ref = fields.Char('Vendor Reference', copy=False,
                              help="Reference of the sales order or bid sent by the vendor. "
                                   "It's used to do the matching when you receive the "
                                   "products as this reference is usually written on the "
                                   "delivery order sent by your vendor.")
    currency_id = fields.Many2one('res.currency', 'Currency', required=True,
                                  default=lambda self: self.env.company.currency_id.id)
    date_approve = fields.Datetime('Confirmation Date', readonly=1, index=True, copy=False)
    date_planned = fields.Datetime(
        string='Receipt Date', index=True, copy=False,  store=True, readonly=False,
        help="Delivery date promised by vendor. This date is used to determine expected arrival of products.")

    import_purchase_line = fields.One2many('import.purchase.line', 'line_id', string='Import Lines', copy=True)

    amount_untaxed = fields.Monetary(string='Untaxed Amount', store=True, readonly=True,
                                     tracking=True)
    amount_tax = fields.Monetary(string='Taxes', store=True, readonly=True)
    amount_total = fields.Monetary(string='Total', store=True, readonly=True)

class ImportPurchaseLine(models.Model):
    _name = "import.purchase.line"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Import Purchase Line"

    line_id=fields.Many2one("import.purchase", string='Import Reference', index=True, required=True, ondelete='cascade')
    product_id = fields.Many2one('product.product', string="Item Details")
    product_qty=fields.Integer(string="Qty.")
    rate=fields.Float(string="Rate $")
    total_usd=fields.Float(string="Total USD")
    conv_rate=fields.Float(string="Conv. Rate")
    aed_amount=fields.Float(string="AED")
    labour_aed=fields.Float(string="Labour AED")
    freight_aed=fields.Float(string="Labour AED")
    clearance_aed=fields.Float(string="Clearance AED")
    bank_other_changes_aed=fields.Float(string="Bank/Other Changes AED")
    per_unit_aed=fields.Float(string="Item Cost/Unit AED")
    stock_valuation=fields.Float(string="Stock Valuation")


