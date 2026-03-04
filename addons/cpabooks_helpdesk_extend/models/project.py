from odoo import api, models,  fields, _


class Task(models.Model):
    _inherit = "project.task"

    @api.onchange('project_id')
    def onchange_project_id(self):
        for rec in self:
            return {'domain': {'parent_id': [('project_id', '=', rec.project_id.id)]}}

    # project_id = fields.Many2one('project.project', string='Project',
    #     compute='_compute_project_id', store=True, readonly=False,
    #     index=True, tracking=True, check_company=True, change_default=True)
    # parent_id = fields.Many2one('project.task', string='Parent Task', index=True)


class Planning(models.Model):
    _inherit = 'planning.slot'

    # @api.model
    # def create(self, vals_list):
    #     vals_list = super(Planning, self).create(vals_list)
    #
    #     if vals_list.allocated_hours:
    #         self.env['account.analytic.line'].search([('employee_id','=',vals_list.employee_id.id)], limit=1).sudo().write({'plan_time': vals_list.allocated_hours})
    #     else:
    #         self.env['account.analytic.line'].search([('employee_id','=',vals_list.employee_id.id)], limit=1).sudo().write({'plan_time': 1.00})
    #
    #     return vals_list

