from odoo import models, fields, api, _


class StockMove(models.Model):
    _inherit = 'stock.move'

    remarks=fields.Text(string="Remarks")
