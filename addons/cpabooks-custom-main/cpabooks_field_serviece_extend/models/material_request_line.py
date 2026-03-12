from odoo import models, fields, api, _

class MaterialRequestLine(models.Model):
    _name = 'material.request.line'
    _description = 'Material Request Line'

    task_id = fields.Many2one('project.task', string='Task', ondelete='cascade')
    product_id = fields.Many2one('product.product', string='Product', required=True)
    description = fields.Char(string='Description')
    quantity = fields.Float(string='Quantity', default=1.0)
    quantity_done = fields.Float(string='Done Quantity', compute='get_quantity_done')

    def get_quantity_done(self):
        for rec in self:
            rec.quantity_done = 0.0
            if rec.task_id:
                picking = self.env['stock.picking'].search([('issue_project_task_id', '=', rec.task_id.id)], limit=1)
                for move in picking.move_ids_without_package:
                    rec.quantity_done = move.quantity_done



    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id and not self.description:
            self.description = self.product_id.display_name
