from odoo import api, models, fields, _
from odoo.exceptions import UserError

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    origin = fields.Char(
        'Source Document', index=True,
        states={'done': [('readonly', True)], 'cancel': [('readonly', True)]},
        help="Reference of the document")

    project_id = fields.Many2one('project.project', 'Project')
    is_project_id = fields.Boolean('Is Project Id', default=True)

    @api.model
    def create(self, vals_list):
        res = super(StockPicking, self).create(vals_list)
        qt = self.env['sale.order'].search([('name', '=', vals_list.get('origin'))], limit=1)
        if qt:
            res.is_project_id = qt.is_project_create
        return res

    def set_project_id(self):
        for rec in self:
            project = self.env['project.project'].search([('name', '=', rec.origin)], limit=1)
            if project:
                rec.project_id = project.id
                rec.is_project_id = False
            else:
                raise UserError(_("No project found with the name of '%s'") % rec.origin)
