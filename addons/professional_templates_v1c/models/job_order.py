from odoo import api, models, fields, _


# class JobOrder(models.Model):
#     _inherit = 'quotation.job.order'
#
#
#     def action_confirmed(self):
#         for rec in self:
#             vals = super(JobOrder, self).action_confirmed()
#             rec.quotation_no.job = rec.name
#             return vals
#
#     def action_create_delivery(self):
#         for rec in self:
#             vals = super(JobOrder, self).action_create_delivery()
#             delivery = self.env['stock.picking'].sudo().search([('job_order_id', '=', self.id)], limit=1)
#             rec.quotation_no.delivery = delivery.name
#             return vals




