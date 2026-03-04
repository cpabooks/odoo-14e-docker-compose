import datetime

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class AccountMoveInherit(models.Model):
    _inherit = 'account.move'

    job_order_ids=fields.Many2many('quotation.job.order',string='Job Order No.')
    show_job_no = fields.Boolean(string="Show Job No.")

    @api.onchange('invoice_origin')
    def set_job_order(self):
        for rec in self:
            rec.job_order_ids =None
            if rec.invoice_origin and rec.move_type=='outgoing':
                get_all_job_orders=self.env['quotation.job.order'].sudo().search([('quotation_no','=',self.env['sale.order'].sudo().search([('name','=',rec.invoice_origin)],limit=1).id)])
                rec.job_order_ids=[(6,0,get_all_job_orders.ids)]

    @api.onchange('company_id')
    def get_default_job_no(self):
        get_highest_inv = self.env['account.move'].sudo().search(
            [('company_id', '=', self.company_id.id), ('move_type', '=', 'out_invoice'), ('state', '!=', 'cancel')],
            limit=1,
            order='id desc')

        if get_highest_inv:
            self.show_job_no = get_highest_inv.show_job_no
