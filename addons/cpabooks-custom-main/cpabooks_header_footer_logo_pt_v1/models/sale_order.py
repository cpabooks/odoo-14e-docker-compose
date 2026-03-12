from odoo import api, models, fields, _

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    is_hide_header_footer = fields.Boolean('Hide Header Footer')