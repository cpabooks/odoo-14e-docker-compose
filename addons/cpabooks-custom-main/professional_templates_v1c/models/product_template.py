from odoo import fields, models, api, _
from odoo.exceptions import UserError, AccessError, ValidationError, RedirectWarning

class ProductTemplateInherit(models.Model):
    _inherit = 'product.template'

    company_id = fields.Many2one(
        'res.company', 'Company', index=1)

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

    item_code = fields.Char(string='Item Code')
    default_code = fields.Char('Part Number', index=True)
    prod_description = fields.Text('Description')
    delivery_prod_description = fields.Text('Delivery Description')
    item_code_old = fields.Char('Item Code Old')

    # @api.model
    # def set_all_prod_description(self):
    #     all_prod_ids = self.search([])
    #     for prod_id in all_prod_ids:
    #         if not prod_id.prod_description and prod_id.description:
    #             prod_id.write({
    #                 'prod_description': prod_id.description
    #             })
    #         elif not prod_id.prod_description

    def action_reset_item_code(self):
        all_categ = self.env['product.category'].sudo().search([])
        for categ in all_categ:
            categ.code_next = 1

        products = self.search([])
        for product in products:
            if product.categ_id:
                product.item_code = product.categ_id.get_next_code()

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

    @api.model
    def create(self, vals):
        res = super(ProductTemplateInherit, self).create(vals)
        if res.categ_id:
            res.item_code = res.categ_id.get_next_code()
        return res

    def write(self, vals):
        res = super(ProductTemplateInherit, self).write(vals)
        print(res)
        if vals.get('categ_id'):
            for rec in self:
                rec.item_code = rec.categ_id.get_next_code()
        return res

    @api.model
    def _name_search(self, name='', args=None, operator='ilike', limit=100, name_get_uid=None):
        args = args or []
        domain = []
        if name:
            domain = ['|', ('item_code', operator, name), ('name', operator, name)]
        return self._search(domain + args, limit=limit, access_rights_uid=name_get_uid)

    def name_get(self):
        name_lst = []
        for rec in self:
            if rec.item_code:
                name = f'[{rec.item_code}] {rec.name}'
            else:
                name = f'{rec.name}'
            name_lst += [(rec.id, name)]
        return name_lst

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

