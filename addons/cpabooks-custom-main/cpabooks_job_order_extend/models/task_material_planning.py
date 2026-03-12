from odoo import fields, models, api


class TaskMaterialPlanning(models.Model):
    _name = 'task.material.planning'

    sub_task_id = fields.Many2one('product.product', string='Sub Task')
    task_id = fields.Many2one('product.category', string='Task')
    task_job_order_id = fields.Many2one('job.order', 'Task Job order')

    @api.onchange('sub_task_id')
    def _onchange_sub_task_id(self):
        self.task_id = self.sub_task_id.categ_id
