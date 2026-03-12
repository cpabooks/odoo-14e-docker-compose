from odoo import api, models, fields, _

class TimesheetTemplateConfigResult(models.TransientModel):
    _name = 'timesheet.templates.config.result'
    _description = 'Timesheet Template Configuration Result'

    message = fields.Text('Message')
