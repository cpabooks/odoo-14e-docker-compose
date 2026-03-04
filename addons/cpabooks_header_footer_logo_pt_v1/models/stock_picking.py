from odoo import api, models, fields, _

class StockPiking(models.Model):
    _inherit = 'stock.picking'

    is_hide_header_footer = fields.Boolean('Hide Header Footer')