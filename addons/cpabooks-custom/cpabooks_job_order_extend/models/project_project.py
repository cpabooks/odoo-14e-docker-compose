from odoo import fields, models, api


class ProjectProject(models.Model):
    _inherit = 'project.project'



    @api.model
    def create(self, vals):
        res = super(ProjectProject, self).create(vals)
        task_seq = 1
        default_task = self.env['project.default.task'].search([])
        for task in default_task:
            sub_task_lines = []
            if not task.parent_id:
                stage_id = self.env.ref("cpabooks_job_order_extend.project_task_type_stage_main_task")
                # stage_id.project_ids = [(4, res.id)]
                #
                # # stage_id.project_ids = [(4, res.id)]
                stage_id_under_progress = self.env.ref(
                    "cpabooks_job_order_extend.project_task_type_stage_task_under_progress")
                # stage_id_under_progress.project_ids = [(4, res.id)]
                #
                stage_id_completed = self.env.ref("cpabooks_job_order_extend.project_task_type_stage_task_competed")
                # stage_id_completed.project_ids = [(4, res.id)]
                #
                stage_sub_task = self.env.ref("cpabooks_job_order_extend.project_task_type_stage_sub_task")
                # stage_sub_task.project_ids = [(4, res.id)]

                parent_task = self.env['project.task'].create({
                    'task_seq': task_seq,
                    'name': task.name,
                    'project_id': res.id,
                    'stage_id': stage_id.id,
                    'task_type':'main'
                })
                sub_task_seq = 0.1

                default_sub_task = self.env['project.default.task'].search([('parent_id', '=', task.id)])
                for sub_task in default_sub_task:
                    sub_task_created = self.env['project.task'].create({
                        'task_seq': task_seq + sub_task_seq,
                        'name': sub_task.name,
                        'task_parent_id': parent_task.id,
                        'is_subtask': True,
                        'stage_id': stage_sub_task.id,
                        'task_type':'sub'
                    })

                    sub_task_seq += 0.10

                task_seq += 1
        return res
