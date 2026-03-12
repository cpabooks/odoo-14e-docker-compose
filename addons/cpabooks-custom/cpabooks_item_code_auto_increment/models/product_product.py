from odoo import fields, models, api
from odoo.osv import expression


class ItemonProduct(models.Model):
    _inherit = 'product.product'

    item_code = fields.Char(string='Item Code', compute='_compute_item_code_field', inverse='_set_item_code_field',
                            store=True , default=lambda x:x._get_default_no())

    def _get_default_no(self):
        get_max_code=self.env['product.product'].sudo().search([('item_code','!=',None)],order='id desc',limit=1)
        number_string=""
        if get_max_code:
            for ch in get_max_code.item_code:
                if ch.isdigit():
                    number_string+=ch
            if number_string=="":
                return "100001"
            else:
                return str(int(number_string)+1)
        else:
            return "100001"