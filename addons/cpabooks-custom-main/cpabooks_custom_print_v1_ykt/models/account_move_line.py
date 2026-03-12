from odoo import fields, models, api


class AccountMoveLineInherit(models.Model):
    _inherit = 'account.move.line'

    uom_text = fields.Char(string="UoM")

    @api.onchange('product_id')
    def set_uom(self):
        for rec in self:
            rec.uom_text = rec.product_id.uom_id.name