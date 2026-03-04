from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError

class QCInherit(models.Model):
    _inherit = "quality.check"

    product_id = fields.Many2one(
        'product.product', 'Product', check_company=True, required=False,
        domain="[('type', 'in', ['consu', 'product']), '|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    
