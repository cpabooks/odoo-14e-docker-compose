# -*- coding: utf-8 -*-

from odoo import api,models, fields

class SaleOrder(models.Model):

    _inherit = "sale.order"

    markup = fields.Float(string='Total Markup', store=True)
    estimate_id = fields.Many2one('sale.estimate.job',string='Estimate')

class SaleOrderLine(models.Model):

    _inherit = "sale.order.line"

    estimate_bool = fields.Boolean(default=False)
    markup = fields.Float(string='Markup', store=True)
    job_type = fields.Selection(
        selection=[('material', 'Material'),
                   ('labour', 'Labour'),
                   ('overhead', 'Overhead'),
                   ('consumable', 'Consumable'),
                   ('logistics', 'Logistics'),
                   ('outsourced', 'Outsourced'),
                   ('estimation', 'Estimation'),
                   ('other', 'Others')
                   ],
        string="Type",

    )

class HrEmployeePrivate(models.Model):

    _inherit = "hr.employee"

    hourly_cost = fields.Float(string="Hourly Cost")
    product_id = fields.Many2one('product.product',string='Related Product',)

class FleetVehicle(models.Model):
    _inherit = 'fleet.vehicle'

    price_per_kilometer = fields.Float(string="Price/Km")
    product_id = fields.Many2one('product.product',string='Related Product',)

