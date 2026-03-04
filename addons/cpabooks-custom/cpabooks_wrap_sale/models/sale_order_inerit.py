from odoo import api, fields, models, _


class SaleOrderLine(models.Model):
    _name = 'sale.order.line'
    _inherit = ['sale.order.line']

    name = fields.Text(string='Description', required=True)


