from odoo import api, models, fields, _


class SaleOrder(models.Model):
    _inherit = 'sale.order'