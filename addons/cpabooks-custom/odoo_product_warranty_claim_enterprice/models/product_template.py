# -*- coding: utf-8 -*-

from odoo import models, fields


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    custom_allow_warranty = fields.Boolean(
        string='Allow Warranty',
        copy=True,
    )
    custom_renew_warranty = fields.Boolean(
        string='Allow Warranty Renew',
        copy=True,
    )
    custom_warranty_type = fields.Selection([
        ('free', 'Free Warranty'),
        ('paid', 'Paid Warranty'),
        ],
        default='free',
        copy=True,
    )
    custom_warranty_cost = fields.Float(
        string='Warranty Cost',
        copy=True,
    )
    custom_warranty_rule_type = fields.Selection([
        ('daily', 'Day(s)'),
        ('weekly', 'Week(s)'),
        ('monthly', 'Month(s)'),
        ('yearly', 'Year(s)')],
        default='monthly',
        string='Warranty Period',
        copy=True,
    )
    custom_warranty_interval = fields.Integer(
        string="Warranty Repeat",
        copy=True,
    )

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: