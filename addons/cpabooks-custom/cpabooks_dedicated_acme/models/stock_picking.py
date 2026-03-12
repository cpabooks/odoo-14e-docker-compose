from odoo import fields, models


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    lpo_number=fields.Char(string="LPO")

    print_manual_dn = fields.Boolean(string="Print Manual Delivery Note?")

    manual_dn = fields.Char(string="Manual Delivery Note")
