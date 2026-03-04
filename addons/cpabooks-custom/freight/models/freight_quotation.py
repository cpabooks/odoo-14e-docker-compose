
from odoo import api, fields, models, tools, SUPERUSER_ID, _

class FreightQuotation(models.Model):
    _name= 'freight.quotation'
    _description= 'Freight Quoation'

    name = fields.Char(string='Name', copy=False)
    quotation_date = fields.Datetime(string='Quotation Date', required=True, default=fields.Datetime.now, help="Creation")
    direction = fields.Selection(([('import','Import'),('export','Export'),('crosstrade','Crosstrade')]), string='Direction')
    transport = fields.Selection(([('air','Air'),('ocean','Ocean'),('land','Land')]), string='Transport')
    operation = fields.Selection([('direct', 'Direct'), ('house', 'House'), ('master', 'Master')], string='Operation')
    ocean_shipment_type = fields.Selection(([('fcl','FCL'),('lcl','LCL')]), string='Ocean Shipment Type')
    inland_shipment_type = fields.Selection(([('ftl','FTL'),('ltl','LTL')]), string='Inland Shipment Type')
    shipper_id = fields.Many2one('res.partner', 'Customer')
    consignee_id = fields.Many2one('res.partner', 'Vendor')
    source_location_id = fields.Many2one('freight.port', 'POL', index=True)
    source_flag_url = fields.Char("Flag", related="source_location_id.country.image_url")
    destination_flag_url = fields.Char("Flag", related="destination_location_id.country.image_url")
    country_id = fields.Many2one('res.country', 'Country')
    destination_location_id = fields.Many2one('freight.port', 'POD', index=True)
    button_sale_quote_to_freight = fields.Char('Creare Freight')
    margin = fields.Float("Margin", compute='compute_total_amount')
    invoice_residual = fields.Float('Invoice Residual',compute='compute_total_amount')
    bills_residual = fields.Float('Bills Residual', compute='compute_total_amount')
    invoice_paid_amount = fields.Float('Invoice', compute='compute_total_amount')
    bills_paid_amount = fields.Float('Bills', compute='compute_total_amount')
    actual_margin = fields.Float('Actual Margin', compute='compute_total_amount')

    freight_month = fields.Selection([('january', 'January'), ('february', 'February'), ('march', 'March'), ('april', 'April'),
                              ('may', 'May'), ('june', 'June'), ('july', 'July'), ('august', 'August'),
                              ('september', 'September'), ('october', 'October'), ('november', 'November'), ('december', 'December')],
                             string='Month')
    freight_bill_of_ladding = fields.Char("Bill of Ladding")
    freight_container_no = fields.Char("Container No.")
    freight_booking_no = fields.Char("Booking No.")

    operation_id = fields.Many2one('freight.operation', string='Operation ID')
    product_id = fields.Many2one('product.product', 'Product')
    port_of_loading = fields.Many2one('freight.port', string="POL")
    port_of_delivery = fields.Many2one('freight.port', string="POD")

    product_uom_qty = fields.Float('Qty')
    product_uom = fields.Many2one('uom.uom', 'Unit')
    price_unit = fields.Float('Unit Price')
    price_subtotal = fields.Float('Sub Total')
    freight_item_qty = fields.Integer("Vol. Qty")
    freight_container_type = fields.Many2one('freight.container.type', "container Type")
    # freight_container_type = fields.Selection(
    #     [('2000', '20 STD'), ('4000', '40 STD'), ('4001', '40 HC'), ('4002', '45 HC'), ('2001', '20 Reefer'),
    #      ('4003', '40 Reefer'), ('2002', '20 Open Top'), ('4004', '40 Open Top'), ('4005', '40 Open Top High'),
    #      ('2003', '20 Flat'), ('4006', '40 Flat')], string='Cont. Type', default='2000')
    freight_teus20ft = fields.Float(string="TEUS 20ft", digits=(12, 1))
    freight_ffe40ft = fields.Float(string="FFE 40ft", digits=(12, 1))
    freight_etd = fields.Date(string='ETD')
    rate_validity = fields.Date(string='Rate Validity')
    foreign_currency = fields.Many2one('res.currency', string='Currency',
                                       default=lambda self: self.env['res.currency'].search([('name', '=', 'USD')]))
    rate_in_foreign_currency = fields.Float(string='Rate Forex')  # , compute='_compute_currency')
    amount_in_foreign_currency = fields.Float(string='Amt. Forex')  # , compute='_compute_currency')
