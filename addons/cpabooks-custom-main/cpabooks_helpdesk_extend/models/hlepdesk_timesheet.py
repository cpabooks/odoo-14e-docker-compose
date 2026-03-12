from odoo import api, models, fields, _


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'


    name = fields.Text('Description', required=True)

    module_id = fields.Many2one('ir.module.module', 'Module',default=lambda self: self.get_tech_name())
    tech_module = fields.Char(string='Module Technical Name', related='module_id.name',default=lambda self: self.get_tech_name())
    sub_task = fields.Many2one('project.task', 'Sub Task')

    @api.onchange('product_id')
    def get_tech_name(self):
        for rec in self:
            rec.tech_module = rec.helpdesk_ticket_id.module_id.name









