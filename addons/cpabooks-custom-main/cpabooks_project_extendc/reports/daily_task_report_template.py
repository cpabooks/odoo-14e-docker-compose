from odoo import models, api, fields
from datetime import datetime, timedelta


class TaskReport(models.AbstractModel):
    _name = 'report.cpabooks_project_extend.daily_task_report_template'
    _description = 'Task Report Renderer'

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['task.report.wizard'].browse(docids)
        return {
            'doc_ids': docids,
            'doc_model': 'task.report.wizard',
            'docs': docs,
            'data': data,
            'user': data.get('user', False),
            # 'tasks': tasks
        }