from odoo import api, models, fields, _

class MaintenanceTenant(models.Model):
    _name = 'maintenance.tenant'
    _description = 'Maintenance Tenant'
    _order = 'id asc'
    _rec_name = 'name'

    name = fields.Char('Name', required=True)
    email = fields.Char('Email')
    mobile = fields.Char('Mobile')
    analytical_account_id = fields.Many2one("account.analytic.account", "Building")
    project_id = fields.Many2one("project.project", "Project")
    task_id = fields.Many2one("project.task", "Flat/Villa No.")