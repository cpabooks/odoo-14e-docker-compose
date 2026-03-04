# -*- coding: utf-8 -*-

from odoo import fields, models, _, api


class FreightInquiry(models.Model):
    _name = 'freight.inquiry'
    _description = 'Freight Inquiry'

    customer_id = fields.Many2one('res.partner', 'Customer')
    freight_inquiry_line_ids = fields.One2many('freight.inquiry.line', 'inquiry_id')

class FreightInquiryLine(models.Model):
    _name = 'freight.inquiry.line'
    _description = 'Freight Inquiry Line'

    inquiry_id = fields.Many2one('freight.inquiry', string='Inquiry ID')
    product_id = fields.Many2one('product.product', 'Product')
    port_of_loading = fields.Many2one('freight.port', string="POL")
    port_of_delivery = fields.Many2one('freight.port', string="POD")

    freight_20ge = fields.Float(string="20 GE", digits=(12,1),store=True)
    freight_40ge = fields.Float(string="40 GE", digits=(12,1), store=True)
    freight_40hc = fields.Float(string="40 HC", digits=(12,1), store=True)



    # freight_teus20ft = fields.Float(string="TEUS 20ft", digits=(12,1))
    # freight_ffe40ft = fields.Float(string="FFE 40ft", digits=(12,1))
    # freight_etd = fields.Date(string='ETD')
    # rate_validity = fields.Date(string='Rate Validity')
    # freight_item_qty = fields.Integer("Vol. Qty", store=True)
    # price_unit = fields.Float('Unt Rate (AED)')
    # price_subtotal = fields.Float('Amount (AED)')
    # product_uom_qty = fields.Float('Qty', default="1")
    # foreign_currency = fields.Many2one('res.currency', string='Curr.', store=True,
    #                                    default=lambda self: self.env['res.currency'].search([('name', '=', 'USD')]))
    # ex_currency_rate = fields.Float(string='Ex Rate', compute='_compute_ex_currency')
    #
    # rate_as_currency = fields.Float(string='Rate Forex', compute='_compute_currency', inverse='_inverse_price_unit')
    # amount_as_currency = fields.Float(string='Amt. Forex', compute='_compute_currency')
    #








































































