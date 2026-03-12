import re

from reportlab.graphics.renderbase import inverse

from odoo import fields, models, api
from odoo.osv import expression


class ItemonProduct(models.Model):
    _inherit = 'product.product'

    item_code = fields.Char(string='Item Code', compute='_compute_item_code_field', inverse='_set_item_code_field',
                            store=True)
    # item_code = fields.Char(string='Item Code', index=True)
    default_code = fields.Char('Part Number', index=True)
    prod_description = fields.Text('Product Description', inverse='_set_prod_description',
                                   compute='_get_product_description', store=True, readonly=False)
    delivery_prod_description = fields.Text('Delivery Description', inverse='_set_delivery_prod_description',
                                            compute='_get_delivery_product_description', store=True, readonly=False)
    item_code_old = fields.Char('Item Code old', compute='_get_item_code_old', inverse='_set_item_code_old')

    # def get_product_multiline_description_sale(self):
    #     for rec in self:
    #         if rec.prod_description:
    #             return rec.prod_description
    #         else:
    #             return rec.name

    # @api.model
    # def create(self, vals):
    #     res = super(ItemonProduct, self).create(vals)
    #     if res.categ_id:
    #         res.item_code = res.categ_id.get_next_code()
    #     return res
    #
    # def write(self, vals):
    #     res = super(ItemonProduct, self).write(vals)
    #     print(res)
    #     if vals.get('categ_id'):
    #         for rec in self:
    #             rec.item_code = rec.categ_id.get_next_code()
    #     return res

    @api.depends('product_tmpl_id.item_code_old')
    def _get_item_code_old(self):
        for rec in self:
            rec.item_code_old = rec.product_tmpl_id.item_code_old

    def _set_item_code_old(self):
        for rec in self:
            rec.product_tmpl_id.item_code_old = rec.item_code_old

    @api.depends('product_tmpl_id.item_code')
    def _compute_item_code_field(self):
        for product in self:
            product.item_code = product.product_tmpl_id.item_code

    def _set_item_code_field(self):
        for product in self:
            product.product_tmpl_id.item_code = product.item_code

    @api.depends('product_tmpl_id.prod_description')
    def _get_product_description(self):
        for product in self:
            product.prod_description = product.product_tmpl_id.prod_description

    def _set_prod_description(self):
        for rec in self:
            rec.product_tmpl_id.prod_description = rec.prod_description

    def _set_delivery_prod_description(self):
        for rec in self:
            rec.product_tmpl_id.delivery_prod_description = rec.delivery_prod_description

    @api.depends('product_tmpl_id.delivery_prod_description')
    def _get_delivery_product_description(self):
        for product in self:
            product.delivery_prod_description = product.product_tmpl_id.delivery_prod_description

    # def name_get(self):
    #     result = []
    #     for record in self:
    #         display_name=record.name
    #         if record.default_code:
    #             display_name='[' + record.default_code + ']'+display_name
    #         # Customize as needed
    #         if record.item_code:
    #             display_name ='['+record.item_code+']'+display_name
    #         result.append((record.id, display_name))
    #     return result
    #

    # @api.model
    # def _name_search(self, name='', args=None, operator='ilike', limit=100, name_get_uid=None):
    #     # Call the original _name_search function to get the initial search result
    #     product_ids = super(ItemonProduct, self)._name_search(name=name, args=args, operator=operator, limit=limit,name_get_uid=name_get_uid)
    #
    #     # Add your additional search criteria here
    #     # if name:
    #     #     extra_domain = [('item_code', operator, name)]
    #     #     product_ids += list(self._search(args + extra_domain, limit=limit))
    #
    #
    #     return product_ids

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