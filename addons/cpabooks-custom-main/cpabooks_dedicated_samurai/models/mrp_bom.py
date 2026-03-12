import datetime
from copy import deepcopy

from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.tests import Form
from odoo.tools import float_round



class MRPBoM(models.Model):
    _inherit = 'mrp.bom'

    product_id = fields.Many2one(
        'product.product', 'Product Variant',
        check_company=True,
        domain="[('type', '=', 'product'),  '|', ('company_id', '=', False), ('company_id', '=', company_id)]",
        help="If a product variant is defined the BOM is available only for this product.")

    @api.onchange("product_id")
    def set_product_tmpl(self):
        for rec in self:
            rec.product_tmpl_id=rec.product_id.product_tmpl_id.id