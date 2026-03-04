from odoo import api, models, fields, _


class MaintenanceRequest(models.Model):
    _inherit = 'maintenance.request'

    ticket_no = fields.Char('Ticket No.')
    tenant_id = fields.Many2one('maintenance.tenant', 'Tenant')
    building = fields.Char('Building')
    flat = fields.Char('Flat')
    work_type = fields.Char('Work Type')
    problem = fields.Char('Problem')
    property = fields.Char('Property')
    address = fields.Char('Address')
    partner_id = fields.Many2one('res.partner', 'Customer')
    project_id = fields.Many2one('project.project', "Project")
    city = fields.Char("City/Region")
    analytical_account_id = fields.Many2one("account.analytic.account", "Building")
    task_id = fields.Many2one("project.task", "Flat/Villa No.")

    @api.model
    def create(self, vals):
        res = super().create(vals)
        res.ticket_no = self.env['ir.sequence'].next_by_code('seq.maintenance.request')
        return res
