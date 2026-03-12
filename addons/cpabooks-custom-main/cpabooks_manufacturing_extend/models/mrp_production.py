import datetime
from copy import deepcopy

from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.tests import Form
from odoo.tools import float_round



class MRPProduction(models.Model):
    _inherit = 'mrp.production'

    do_id=fields.Many2one('stock.picking',string="Delivery")