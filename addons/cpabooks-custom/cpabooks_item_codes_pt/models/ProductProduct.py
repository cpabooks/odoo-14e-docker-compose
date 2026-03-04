import re

from odoo import fields, models, api
from odoo.osv import expression


class ItemonProduct(models.Model):
    _inherit = 'product.product'

    item_code = fields.Char(string='Item Code', compute='_compute_item_code_field', inverse='_set_item_code_field',store=True)
    # item_code = fields.Char(string='Item Code', index=True)
    default_code = fields.Char('Part Number', index=True)

    @api.depends('product_tmpl_id.item_code')
    def _compute_item_code_field(self):
        for product in self:
            product.item_code = product.product_tmpl_id.item_code

    def _set_item_code_field(self):
        for product in self:
            product.product_tmpl_id.item_code = product.item_code

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



    @api.model
    def _name_search(self, name='', args=None, operator='ilike', limit=100, name_get_uid=None):
        # Call the original _name_search function to get the initial search result
        product_ids = super(ItemonProduct, self)._name_search(name=name, args=args, operator=operator, limit=limit,name_get_uid=name_get_uid)

        # Add your additional search criteria here
        # if name:
        #     extra_domain = [('item_code', operator, name)]
        #     product_ids += list(self._search(args + extra_domain, limit=limit))


        return product_ids