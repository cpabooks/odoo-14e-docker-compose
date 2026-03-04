from odoo import api, models, fields, _

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    vendor_vat = fields.Char('Vendor Tax Id.', related='partner_id.vat')
