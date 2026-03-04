from odoo import fields, models


class ProductProduct(models.Model):
    _inherit = 'product.product'

    def name_get(self):
        super(ProductProduct, self).name_get()
        pro_result = []
        for rec in self:
            name = rec.name
            code = rec.item_code
            if code:
                pro_result.append((rec.id, '[%s] - %s' % (rec.item_code,rec.name)))
            else:
                pro_result.append((rec.id, '%s' % (rec.name)))

        return pro_result

