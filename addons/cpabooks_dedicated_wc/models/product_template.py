from odoo import api, models, fields, _


class ProductTemplate(models.Model):
    _inherit = 'product.template'


    @api.model
    def create(self, vals_list):
        res = super(ProductTemplate, self).create(vals_list)
        print(res)
        if not res.description:
            res.write({
                'description':res.name
            })

        return res