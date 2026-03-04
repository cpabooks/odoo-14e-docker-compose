from odoo import fields, models, api


class UoMCounty(models.Model):
    _inherit = 'uom.uom'

    counted_qty = fields.float('Counted Quantity')
    another_uom = fields.Char('Another UoM')
