from odoo import api, models, fields, _

class ProjectProject(models.Model):
    _inherit = 'project.project'

    crm_amount = fields.Float('CRM Amount', default=0.0, compute="_get_crm_amount")

    def _get_crm_amount(self):
        for rec in self:
            crm = self.env['crm.lead'].sudo().search([
                ('project_id', '=', rec.id)
            ], limit=1)
            if crm:
                rec.crm_amount = crm.expected_revenue
            else:
                rec.crm_amount = 0.0