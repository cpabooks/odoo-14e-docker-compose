from odoo import fields, models, api, _
from odoo.exceptions import UserError, AccessError, ValidationError, RedirectWarning

class UomUom(models.Model):
    _inherit = 'uom.uom'

    uom_type = fields.Selection([
        ('bigger', 'Bigger than the reference Unit of Measure'),
        ('reference', 'Reference Unit of Measure for this category'),
        ('smaller', 'Smaller than the reference Unit of Measure')], 'Type',
        default='smaller', required=1)

    category_id = fields.Many2one(
        'uom.category', 'Category', required=True, ondelete='cascade',
        help="Conversion between Units of Measure can only occur if they belong to the same category. The conversion will be made based on the ratios.",default=lambda self:self._get_category())


    system_admin = fields.Boolean(compute="_get_system_admin")

    @api.depends('uom_type')
    def _get_system_admin(self):
        for rec in self:
            if self.env.user.has_group('base.group_system'):
                rec.system_admin = True
            else:
                rec.system_admin = False

    def _get_category(self):
        get_unit=self.env['uom.category'].sudo().search([('name','=','Unit')],limit=1)

        if get_unit:
            return get_unit.id
        else:
            uom=self.env['uom.category'].sudo().create({
                'name': 'Unit'
            })
            return uom.id

    @api.constrains('name')
    def _check_name(self):
        if self.name:
            uom_rec = self.env['uom.uom'].search(
                [('name', '=ilike', self.name), ('id', '!=', self.id)])
            if uom_rec:
                raise UserError(_('Already a Unit of Measure exists with same name'))
