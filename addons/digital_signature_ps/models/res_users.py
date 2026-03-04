from odoo import fields, models, api


class ResUsers(models.Model):
    _inherit = 'res.users'

    user_signature=fields.Binary(string="Signture")
    user_signature_name = fields.Char()

    user_stamp=fields.Binary(string="Stamp")
    user_stamp_name = fields.Char()