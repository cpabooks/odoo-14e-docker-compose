from odoo import models, fields, api

from odoo import models


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    issue_project_task_id = fields.Many2one('project.task', string="Project Task")
    issue_project_id=fields.Many2one(related='issue_project_task_id.project_id',string="Project")
    partner_id=fields.Many2one(related='issue_project_task_id.project_id.partner_id',string="Project")

    @api.onchange('issue_project_id')
    def set_customer(self):
        for rec in self:
            rec.partner_id=rec.issue_project_id.partner_id

class StockMove(models.Model):
    _inherit = 'stock.move'

    rate=fields.Float(related="product_id.standard_price", readonly=False,string="Rate")
    amount=fields.Float(compute="get_amount",string="Amount")

    @api.onchange('qty_done')
    def get_amount(self):
        for rec in self:
            rec.amount=rec.rate*rec.quantity_done

