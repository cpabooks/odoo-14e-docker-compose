from odoo import api, models, fields, _


class StockMove(models.Model):
    _inherit = 'stock.move'

    perfume_type = fields.Char('Type')
    perfume_packaging = fields.Char('Packaging')
    percentage = fields.Float('%')
    remarks = fields.Char('Remarks')