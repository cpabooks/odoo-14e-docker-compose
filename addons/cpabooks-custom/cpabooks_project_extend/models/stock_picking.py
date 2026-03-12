from odoo import fields, models, api, _


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    project_id = fields.Many2one('project.project', string='Job Order')