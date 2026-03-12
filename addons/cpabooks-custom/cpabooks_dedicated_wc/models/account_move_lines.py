from odoo import api, models, fields, _
from odoo.release import product_name


class AccountMoveLines(models.Model):
    _inherit = 'account.move.line'

    name = fields.Text('Label')

    @api.onchange('product_id')
    def get_name(self):
        for rec in self:
            if rec.product_id.description:
                rec.name = f'{rec.product_id.name} \n {rec.product_id.description}'
            else:
                rec.name = f'{rec.product_id.name}'
