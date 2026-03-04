from odoo import fields, models, _


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    job_estimate_id = fields.Many2one('job.estimate', string="Sale Order")
    crm_id=fields.Many2one('crm.lead',string="CRM")


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    type = fields.Char('Type')


