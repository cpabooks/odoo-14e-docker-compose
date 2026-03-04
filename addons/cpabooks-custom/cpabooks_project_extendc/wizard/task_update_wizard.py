from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError


class TaskUpdateWizard(models.TransientModel):
    _name = 'task.update.wizard'
    _description = 'Task Update Wizard'

    name = fields.Char()


    def action_update_tasks(self):
        """TODO: Get active_ids from context and update the names"""
        context = self._context or {}
        if not context:
            raise UserError(_("Please Select Tasks"))
        if context.get('active_model') != 'project.task':
            raise ValidationError(_("This Functionality only applied for Tasks(project.task)"))
        task_ids = self.env['project.task'].browse(context.get('active_ids'))
        for task in task_ids:
            task.name = self.name
            task.action_update_name()
