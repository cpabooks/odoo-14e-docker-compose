from odoo import api, models, fields, _

class ProductTemplates(models.Model):
    _inherit = 'product.template'

    coa_code = fields.Char('COA-Code', readonly=True)

