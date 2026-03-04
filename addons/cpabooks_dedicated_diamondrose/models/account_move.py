from odoo import fields, models, api


class AccountMoveInherit(models.Model):
    _inherit = 'account.move'

    multi_salesman = fields.Many2many('res.users', string="Salesman", default=lambda self: self.env.user.ids)
    multi_sales_team = fields.Many2many('crm.team', string="Sales Team",
                                        default=lambda self: self.env.user.sale_team_id.ids)

class AccountMoveLineInherit(models.Model):
    _inherit = 'account.move.line'

    @api.onchange('product_id')
    def set_description(self):
        for rec in self:
            if rec.product_id:
                if rec.product_id.prod_description:
                    rec.name=rec.product_id.prod_description
