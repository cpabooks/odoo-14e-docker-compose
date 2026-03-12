from odoo import api, models, fields, _
import logging

_logger = logging.getLogger(__name__)

class ProjectTaskType(models.Model):
    _inherit = 'project.task.type'

    @api.model
    def action_create_default_stages(self):
        stages = [
            'To Do',
            'In Progress',
            'This Week',
            'This Month',
            'Hold',
            'Done',
        ]
        for stage in stages:
            try:
                if not self.search([('name', '=', stage)]):
                    self.create({'name': stage})
                    _logger.info(f'Stage create "{stage}"')
                else:
                    _logger.info(f'Stage "{stage}" already exists')
            except Exception as e:
                _logger.error(f'Error while creating {stage}. Error: {e} ')
