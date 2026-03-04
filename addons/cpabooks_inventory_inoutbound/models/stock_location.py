from odoo import api, models, fields, _

class StockLocation(models.Model):
    _inherit = 'stock.location'

    user_ids = fields.Many2many('res.users', string='user',)



class WizardInventoryValuationty(models.TransientModel):
    _inherit = 'wizard.inventory.valuation.qty'


    user_id = fields.Many2one('res.users', 'User')

    @api.onchange('user_id')
    def get_location_ids(self):
        if self.user_id:
            domain = [('user_ids', '=', self.user_id.id)]
            user_locations = self.env['stock.location'].search(domain)
            self.location_ids = [(6, 0, user_locations.ids)]
        else:
            self.location_ids = False

    @api.onchange('user_id')
    def get_default_domain(self):
        for rec in self:
            return {'domain':{'location_ids': [('user_ids','=',rec.user_id.id)]}}


    @api.onchange('company_id')
    def get_default_user_id(self):
        context = self._context
        uid = context.get('uid')
        self.user_id = uid