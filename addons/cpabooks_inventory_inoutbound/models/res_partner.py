from odoo import fields, models, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    allow_location_ids = fields.Many2many('stock.location', string="Allow Location")
    related_user = fields.Many2one('res.users', string="Related User")
    @api.model
    def create(self, vals):
        location = self.env['stock.location'].with_context(company_id=self.env.company.id).search([('name', '=', 'Stock')])
        location_id =False
        if location:
            location_id = location[0].id
        location = self.env['stock.location'].create({
            'name': vals['name'],
            'location_id': location_id,
            'usage': 'internal'
        })
        vals['allow_location_ids'] = [(6, 0, location.ids)]
        return super(ResPartner, self).create(vals)
