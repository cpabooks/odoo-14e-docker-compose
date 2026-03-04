from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.tests import Form
from odoo.tools import float_round



class StockMove(models.Model):
    _inherit = 'stock.move'

    mo_id=fields.Many2one('mrp.production',string="Manufacturing")

