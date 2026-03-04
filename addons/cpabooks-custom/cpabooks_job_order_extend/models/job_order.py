# -*- coding: utf-8 -*-

from odoo import fields, models, api


class JobOrder(models.Model):
    _inherit = "job.order"

    task_material_planing_ids = fields.One2many('task.material.planning', 'task_job_order_id',
                                                "Task Material Planning")

    @api.model
    def create(self, vals):
        project_task = []
        task_material_planing_ids = vals.get('task_material_planing_ids')
        task_seq = 1
        sub_task_seq = 0.1
        for task in task_material_planing_ids:
            task_id = task[2]['task_id']
            if task_id not in project_task:
                project_task.append(task_id)
                task_categ = self.env['product.category'].search([('id', '=', task_id)])
                res = self.env['project.task'].create({
                    'task_seq': task_seq,
                    'name': task_categ.name,
                    'project_id': vals.get('project_id'),
                    'task_ref_id': task_id
                })
                project_task_id = res.id
                task_seq += 1
            else:
                project_task_search = self.env['project.task'].search(
                    [('task_ref_id', '=', task_id), ('project_id', '=', vals.get('project_id'))])
                project_task_id = project_task_search.id
            res_vals = super(JobOrder, self).create(vals)
            # add subtask
            sub_task_id = task[2]['sub_task_id']
            task_product = self.env['product.product'].search([('id', '=', sub_task_id)])
            self.env['project.task'].create({
                'task_seq': task_seq + sub_task_seq,
                'name': task_product.name,
                'project_id': vals.get('project_id'),
                'task_parent_id': project_task_id,
                'task_ref_id': project_task_id,
                'is_subtask': True,
            })
            sub_task_seq += 0.10

        return res_vals


class ProjectTask(models.Model):
    _inherit = 'project.task'
    task_ref_id = fields.Integer()
