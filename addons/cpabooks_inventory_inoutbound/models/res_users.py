from odoo import fields, models, api

class ResUsers(models.Model):
    _inherit = 'res.users'

    allow_operation_type = fields.Many2many("stock.picking.type", string="Allow Warehouse")
