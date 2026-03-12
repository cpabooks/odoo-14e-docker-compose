from odoo import fields, models, api, _
from odoo.exceptions import UserError, AccessError, ValidationError, RedirectWarning

class ProductTemplateInherit(models.Model):
    _inherit = 'product.template'

    company_id = fields.Many2one(
        'res.company', 'Company', index=1, default=lambda self:self.env.company.id)

    type = fields.Selection([
        ('consu', 'Consumable'),
        ('service', 'Service'),
        ('product', 'Storable Product')], string='Product Type', default='product', required=True,
        help='A storable product is a product for which you manage stock. The Inventory app has to be installed.\n'
             'A consumable product is a product for which stock is not managed.\n'
             'A service is a non-material product you provide.')

    system_admin = fields.Boolean(compute="_get_system_admin")

    uom_id = fields.Many2one(
        'uom.uom', 'Unit of Measure',
        default=lambda self:self._get_default_uom_id(), required=True,
        help="Default unit of measure used for all stock operations.")

    uom_po_id = fields.Many2one(
        'uom.uom', 'Purchase Unit of Measure',
        default=lambda self:self._get_default_uom_id(), required=True,
        help="Default unit of measure used for purchase orders. It must be in the same category as the default unit of measure.")

    @api.depends('type')
    def _get_system_admin(self):
        for rec in self:
            if self.env.user.has_group('base.group_system'):
                rec.system_admin = True
            else:
                rec.system_admin = False

    def _get_default_uom_id(self):
        get_unit=self.env["uom.uom"].sudo().search([('name','=','Unit')],limit=1)
        if get_unit:
            return get_unit.id
        else:
            get_unit = self.env['uom.category'].sudo().search([('name', '=', 'Unit')], limit=1)

            if get_unit:
                uom_categ_id=get_unit.id
            else:
                uom = self.env['uom.category'].sudo().create({
                    'name': 'Unit'
                })
                uom_categ_id= uom.id
            uom=self.env["uom.uom"].sudo().create({
                'name':'Unit',
                'category_id':uom_categ_id,
                'factor': 1.0,
                'uom_type': 'smaller',
            })
            return uom.id


    # def create(self, vals_list):
    #     get_product=self.env['product.template'].sudo().search([('name','ilike','%'+vals_list['name']+'%')])
    #     if get_product:
    #         raise ValidationError(_("Already exists in system, You can't create duplicate product"))
    #     else:
    #         return super(ProductTemplateInherit, self).create(vals_list)

    @api.constrains('name')
    def _check_name(self):
        for rec in self:
            if rec.name:
                product_rec = self.env['product.template'].search(
                    [('name', '=ilike', rec.name), ('id', '!=', rec.id),('company_id','=',self.env.company.id)])
                if product_rec:
                    raise UserError(_(f'Already a product exists with same name {rec.name}'))

