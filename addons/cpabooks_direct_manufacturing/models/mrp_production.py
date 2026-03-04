from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError, UserError, AccessError
from odoo.tools import float_is_zero, float_round


class MrpProductionInherit(models.Model):
    _inherit = "mrp.production"

    so_line_id=fields.Many2one('sale.order.line')
    so_id=fields.Many2one('sale.order',string="Sale Order")