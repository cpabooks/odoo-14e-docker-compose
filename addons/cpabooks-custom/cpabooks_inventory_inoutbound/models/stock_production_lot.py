from odoo import fields, models, api, _

class stockProductionLot(models.Model):
    _inherit = "stock.production.lot"

    production_date = fields.Date(string='Production Date', copy=False)
    ref = fields.Char(string='Container', copy=False)
    expiration_date = fields.Datetime(string='Expiration Date', copy=False)
    # container_no = fields.Char(string='Container No')