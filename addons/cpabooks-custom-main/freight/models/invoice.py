

import logging
from itertools import groupby
import pytz
import time
import babel

import base64
import urllib
from odoo.osv.expression import get_unaccent_wrapper
import re

from odoo import api, fields, models, tools, SUPERUSER_ID, _
# from odoo.addons.mail.models.mail_template import format_tz
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tools.translate import html_translate

from datetime import datetime
from datetime import time as datetime_time
from dateutil import relativedelta
from odoo.tools import float_compare, float_is_zero


_logger = logging.getLogger(__name__)


class FreightquotefieldtoAccount(models.Model):
    _inherit = 'account.move.line'

    port_of_loading = fields.Many2one('freight.port', string="POL")
    port_of_delivery = fields.Many2one('freight.port', string="POD")
    invoice_group_id=fields.Many2one("freight.invoice.group")
    # freight_item_qty = fields.Integer("Vol. Qty", store=True)
    rate_basis = fields.Many2one("freight.rate.basis")
    freight_container_size = fields.Many2one("freight.container.size",string="cont.Size")
    freight_container_type = fields.Many2one('freight.container.type', "container Type")
    freight_teus20ft = fields.Float(string="TEUS 20ft", digits=(12, 1), store=True)
    freight_ffe40ft = fields.Float(string="FFE 40ft", digits=(12, 1), store=True)
    rate_validity = fields.Date(string='Rate Validity')
    freight_etd = fields.Date(string='ETD')

    foreign_currency = fields.Many2one('res.currency', string='Curr.', default=lambda self: self.env['res.currency'].search([('name', '=', 'USD')]))
    ex_currency_rate = fields.Float(string='Ex Rate', compute='_compute_ex_currency')
    rate_in_foreign_currency = fields.Float(string='Unt Rate (Forex)', compute='_compute_currency')
    amount_in_foreign_currency = fields.Float(string='Amount (Forex)', compute='_compute_currency')

    @api.onchange('rate_in_foreign_currency')
    def _compute_ex_currency(self):
        for rec in self:
            rec.ex_currency_rate = 1 / rec.foreign_currency.rate

    @api.onchange('foreign_currency', 'price_unit', 'quantity')
    def _compute_currency(self):
        for rec in self:
            rec.rate_in_foreign_currency = rec.price_unit * rec.foreign_currency.rate
            rec.amount_in_foreign_currency = (rec.price_unit * rec.foreign_currency.rate) * rec.quantity


    @api.onchange('quantity', 'freight_container_type')
    def _compute_sum(self):
        for rec in self:
            rec.freight_teus20ft = (rec.quantity * int(rec.freight_container_type)) / 2000
            rec.freight_ffe40ft = (rec.quantity * int(rec.freight_container_type)) / 4000

