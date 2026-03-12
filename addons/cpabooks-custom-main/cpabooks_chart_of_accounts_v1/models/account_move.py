# from odoo import models, fields, api
#
# class AccountMoveLineInherit(models.Model):
#     _inherit="account.move.line"
#
#     @api.onchange('product_id')
#     def get_product_analytic_acc(self):
#         for rec in self:
#             chk_config=self.env['product.analytic.acc.conf'].sudo().search([('item_id','=',rec.product_id.id)],limit=1)
#             if chk_config:
#                 rec.analytic_account_id=chk_config.id