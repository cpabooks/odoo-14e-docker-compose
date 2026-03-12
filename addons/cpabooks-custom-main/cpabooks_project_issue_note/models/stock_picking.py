from odoo import models, fields, api

from odoo import models


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    issue_project_task_id = fields.Many2one('project.task', string="Project Task")
    issue_project_id=fields.Many2one(related='issue_project_task_id.project_id',string="Project")
    partner_id=fields.Many2one(related='issue_project_task_id.project_id.partner_id',string="Project")
    material_line_ids = fields.One2many(
        'material.request.line',
        'task_id',
        compute='_compute_material_line_ids',
        string='Material Lines'
    )

    @api.onchange('issue_project_id')
    def set_customer(self):
        for rec in self:
            rec.partner_id=rec.issue_project_id.partner_id

    def _compute_material_line_ids(self):
        for rec in self:
            if rec.issue_project_task_id:
                rec.material_line_ids = rec.issue_project_task_id.material_line_ids
            else:
                rec.material_line_ids = False

    @api.onchange('issue_project_task_id')
    def _onchange_issue_project_task_id(self):
        """
        Dynamically populate stock moves and partner when a Task is selected.
        This replaces the bad practice of creating DB records inside a compute method.
        """
        for rec in self:
            if rec.issue_project_task_id:

                # 2. Populate Stock Moves
                move_lines = []


                # Clear existing lines to prevent duplicates if the user changes the task
                rec.move_ids_without_package = [(5, 0, 0)]

                # Add lines using the (0, 0, {values}) command tuple
                for material_line in rec.issue_project_task_id.material_line_ids:
                    move_lines.append((0, 0, {
                        'name': material_line.description or material_line.product_id.name,
                        'product_id': material_line.product_id.id,
                        'product_uom_qty': material_line.quantity,
                        'product_uom': material_line.product_id.uom_id.id,
                        'location_id': material_line.product_id.location_id.id
                    }))

                rec.move_ids_without_package = move_lines


class StockMove(models.Model):
    _inherit = 'stock.move'

    rate=fields.Float(related="product_id.standard_price", readonly=False,string="Rate")
    amount=fields.Float(compute="get_amount",string="Amount")

    @api.onchange('qty_done')
    def get_amount(self):
        for rec in self:
            rec.amount=rec.rate*rec.quantity_done

