from odoo import fields, models, api, _
from odoo.exceptions import UserError, AccessError, ValidationError, RedirectWarning


class ResPartnerInherit(models.Model):
    _inherit = 'res.partner'

    company_id = fields.Many2one(
        'res.company', 'Company', index=1)

    # company_id = fields.Many2one(
    #     'res.company', 'Company', index=1, related="create_uid.company_id")

    @api.constrains('name')
    def _check_name(self):
        for rec in self:
            if rec.name:
                partner_rec = self.env['res.partner'].search(
                    [('name', 'ilike', rec.name), ('id', '!=', rec.id),('company_id','=',rec.company_id.id)])
                if partner_rec:
                    raise UserError(_('Already exists with same name'))


