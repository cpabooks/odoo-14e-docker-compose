from odoo import models, fields


class PosConfig(models.Model):
    _inherit = 'pos.config'

    user_ids = fields.Many2many(comodel_name="res.users", string="Authorized Users")
