from odoo import models, fields, api
from odoo.addons.base.models.res_partner import WARNING_MESSAGE, WARNING_HELP
class ProductTemplateInherit(models.Model):
    _inherit="product.template"

    purchase_line_warn = fields.Selection(WARNING_MESSAGE, 'Purchase Order Line Warning',required=False, help=WARNING_HELP, default="no-message")