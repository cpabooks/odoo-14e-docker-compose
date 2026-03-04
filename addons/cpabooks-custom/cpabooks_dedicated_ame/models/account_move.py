from odoo import fields, models, api


class AccountMoveInherit(models.Model):
    _inherit = 'account.move'

    prepare_by = fields.Many2one('res.users', string="Prepare By", default=lambda self: self.env.user.id)