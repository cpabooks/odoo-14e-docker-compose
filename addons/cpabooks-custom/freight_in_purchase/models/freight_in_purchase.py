# -*- coding: utf-8 -*-

from odoo import fields, models, _, api


class PurchaselineInherit(models.Model):
    _inherit = "purchase.order.line"

    shipping_line_id = fields.Many2one('res.partner','Shipping Line')
    agent_id = fields.Many2one('res.partner', 'Agent')
    source_country_id = fields.Many2one('res.country', 'POL', index=True)
    destination_country_id = fields.Many2one('res.country', 'POD', index=True)
    freight_item_qty = fields.Integer("Vol. Qty", store=True)

    freight_container_type = fields.Selection([('2000', '20 STD'), ('4000', '40 STD'), ('4001', '40 HC'), ('4002', '45 HC'), ('2001', '20 Reefer'),
            ('4003', '40 Reefer'), ('2002', '20 Open Top'), ('4004', '40 Open Top'), ('4005', '40 Open Top High'), ('2003', '20 Flat'), ('4006', '40 Flat')], string='Cont. Type', default='2000', store=True)
    freight_teus20ft = fields.Float(string="TEUS 20ft", digits=(12,1), store=True)
    freight_ffe40ft = fields.Float(string="FFE 40ft", digits=(12,1), store=True)
    rate_validity = fields.Date(string='Rate Validity', store=True)
    remarks = fields.Text(string='Remarks')

    @api.onchange('freight_item_qty', 'freight_container_type')
    def _compute_sum(self):
        for rec in self:
            rec.freight_teus20ft = (rec.freight_item_qty * int(rec.freight_container_type)) / 2000
            rec.freight_ffe40ft = (rec.freight_item_qty * int(rec.freight_container_type)) / 4000


    # direction = fields.Selection(([('import', 'Import'), ('export', 'Export'), ('crosstrade', 'Crosstrade')]), string='Direction')
    # transport = fields.Selection(([('air','Air'),('ocean','Ocean'),('land','Land')]), string='Transport')
    # operation = fields.Selection([('direct', 'Direct'), ('house', 'House'), ('master', 'Master')], string='Operation')
    # ocean_shipment_type = fields.Selection(([('fcl','FCL'),('lcl','LCL')]), string='Ocean Shipment Type')
    # inland_shipment_type = fields.Selection(([('ftl','FTL'),('ltl','LTL')]), string='Inland Shipment Type')
    #
    # def _prepare_invoice(self):
    #     res = super(QuotationInherit, self)._prepare_invoice()
    #     res['direction'] = self.direction
    #     res['transport'] = self.transport
    #     res['operation'] = self.operation
    #     res['ocean_shipment_type'] = self.ocean_shipment_type
    #     res['inland_shipment_type'] = self.inland_shipment_type
    #     return res


# class InvoiceInherit(models.Model):
#     _inherit = "account.move"
#
#     direction = fields.Selection(([('import', 'Import'), ('export', 'Export'), ('crosstrade', 'Crosstrade')]), string='Direction')
#     transport = fields.Selection(([('air','Air'),('ocean','Ocean'),('land','Land')]), string='Transport')
#     operation = fields.Selection([('direct', 'Direct'), ('house', 'House'), ('master', 'Master')], string='Operation')
#     ocean_shipment_type = fields.Selection(([('fcl','FCL'),('lcl','LCL')]), string='Ocean Shipment Type')
#     inland_shipment_type = fields.Selection(([('ftl','FTL'),('ltl','LTL')]), string='Inland Shipment Type')



# class QuotationfrfieldInherit(models.Model):
#     _inherit = "sale.order.line"
#
#     port_of_loading = fields.Many2one('freight.port', string="POL", store=True)
#     port_of_delivery = fields.Many2one('freight.port', string="POD", store=True)
#     freight_item_qty = fields.Integer("Vol. Qty", store=True)
#     # freight_item_qty = fields.Integer("Vol. Qty", store=True, default={'field':1})
#
#     freight_container_type = fields.Selection([('2000', '20 STD'), ('4000', '40 STD'), ('4001', '40 HC'), ('4002', '45 HC'), ('2001', '20 Reefer'),
#             ('4003', '40 Reefer'), ('2002', '20 Open Top'), ('4004', '40 Open Top'), ('4005', '40 Open Top High'), ('2003', '20 Flat'), ('4006', '40 Flat')], string='Cont. Type', default='2000', store=True)
#     freight_teus20ft = fields.Float(string="TEUS 20ft", digits=(12,1), store=True)
#     freight_ffe40ft = fields.Float(string="FFE 40ft", digits=(12,1), store=True)
#     rate_validity = fields.Date(string='Rate Validity', store=True)
#
#     amount_as_currency = fields.Float(string='Amt Fr.Currency')
#
#     # amount_as_currency = fields.Float(string='Amt Fr.Currency', compute='_compute_currency', store=True)
#     # foreign_currency = fields.Many2one('res.currency', string='Currency', store=True)
#     foreign_currency = fields.Many2one('res.currency', string='Currency', store=True, default=lambda self: self.env['res.currency'].search([('name', '=', 'USD')]))
#
#     @api.onchange('foreign_currency', 'price_unit')
#     def _compute_currency(self):
#         for rec in self:
#             rec.amount_as_currency = rec.price_unit * 0.27



    # def _prepare_invoice_line(self, **optional_values):
    #     self.ensure_one()
    #     res = {
    #         'display_type': self.display_type,
    #         'sequence': self.sequence,
    #         'name': self.name,
    #         'product_id': self.product_id.id,
    #         'product_uom_id': self.product_uom.id,
    #         'quantity': self.qty_to_invoice,
    #         'discount': self.discount,
    #         'price_unit': self.price_unit,
    #         'tax_ids': [(6, 0, self.tax_id.ids)],
    #         'analytic_account_id': self.order_id.analytic_account_id.id,
    #         'analytic_tag_ids': [(6, 0, self.analytic_tag_ids.ids)],
    #         'sale_line_ids': [(4, self.id)],
    #         'port_of_loading': self.port_of_loading,
    #         'port_of_delivery': self.port_of_delivery,
    #         'freight_item_qty': self.freight_item_qty,
    #         'freight_container_type': self.freight_container_type,
    #         'freight_teus20ft': self.freight_teus20ft,
    #         'freight_ffe40ft': self.freight_ffe40ft,
    #         'rate_validity': self.rate_validity,
    #         'amount_as_currency': self.amount_as_currency,
    #         'foreign_currency': self.foreign_currency,
    #
    #     }
    #     if optional_values:
    #         res.update(optional_values)
    #     if self.display_type:
    #         res['account_id'] = False
    #     return res

#
# class CurrencyInherit(models.Model):
#     _inherit='res.currency'
#
#
# class FreightquotefieldtoAccount(models.Model):
#     _inherit = 'account.move.line'
#
#     port_of_loading = fields.Many2one('freight.port', string="POL")
#     port_of_delivery = fields.Many2one('freight.port', string="POD")
#
#     freight_item_qty = fields.Integer("Vol. Qty", store=True)
#     freight_container_type = fields.Selection(
#         [('2000', '20 STD'), ('4000', '40 STD'), ('4001', '40 HC'), ('4002', '45 HC'), ('2001', '20 Reefer'),
#          ('4003', '40 Reefer'), ('2002', '20 Open Top'), ('4004', '40 Open Top'), ('4005', '40 Open Top High'),
#          ('2003', '20 Flat'), ('4006', '40 Flat')], string='Cont. Type', default='2000')
#     freight_teus20ft = fields.Float(string="TEUS 20ft", digits=(12, 1), store=True)
#     freight_ffe40ft = fields.Float(string="FFE 40ft", digits=(12, 1), store=True)
#     rate_validity = fields.Date(string='Rate Validity')
#     amount_as_currency = fields.Float(string='Amt Fr.Currency')
#     foreign_currency = fields.Many2one('res.currency', string='Currency', default=lambda self: self.env['res.currency'].search([('name', '=', 'USD')]))
#
#     @api.onchange('foreign_currency', 'price_unit')
#     def _compute_currency(self):
#         for rec in self:
#             rec.amount_as_currency = rec.price_unit * 0.27
#
#
#
#     @api.onchange('freight_item_qty', 'freight_container_type')
#     def _compute_sum(self):
#         for rec in self:
#             rec.freight_teus20ft = (rec.freight_item_qty * int(rec.freight_container_type)) / 2000
#             rec.freight_ffe40ft = (rec.freight_item_qty * int(rec.freight_container_type)) / 4000



