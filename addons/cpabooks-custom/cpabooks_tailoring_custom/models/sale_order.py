from odoo import models, fields, api


class SaleOder(models.Model):
    _inherit = 'sale.order'

    is_create_project = fields.Boolean('Create Project')
    project_id = fields.Many2one('project.project', string='Project')

    @api.model
    def create(self, vals):
        res = super(SaleOder, self).create(vals)
        if res.is_create_project:
            project = self.env['project.project'].create({
                'name': res.display_name
            })
            res.write({
                'project_id': project.id
            })
        return res
