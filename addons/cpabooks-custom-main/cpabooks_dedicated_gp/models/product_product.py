import re

from odoo import fields, models, api
from odoo.osv import expression


class ProductInherit(models.Model):
    _inherit = 'product.product'

    @api.model
    def _name_search(self, name='', args=None, operator='ilike', limit=100, name_get_uid=None):
        # Call the original _name_search function to get the initial search result
        product_ids = super(ProductInherit, self)._name_search(name=name, args=args, operator=operator, limit=limit,
                                                                name_get_uid=name_get_uid)

        # Add your additional search criteria here
        if name:
            extra_domain = ['|','|',('prod_description', operator, name),('prod_inspiration', operator, name),('item_code',operator,name)]
            product_ids += list(self._search(args + extra_domain, limit=limit))

        return product_ids