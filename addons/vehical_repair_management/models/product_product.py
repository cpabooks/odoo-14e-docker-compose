from odoo import api, models, fields, _

class ProductProduct(models.Model):
    _inherit = 'product.product'

    def name_get(self):
        name = []
        for rec in self:
            if rec.item_code:
                name.append((rec.id, '%s - %s'%(rec.item_code, rec.name)))
            else:
                name.append((rec.id, '%s'%(rec.name)))
        return name

    @api.model
    def name_search(self, name='', args=[], operator='ilike', limit=100):
        """
        Added name_search for purpose to search by name and code
        @param self: The object pointer.
        """

        args += ['|', ('name', operator, name), ('item_code', operator, name)]
        cuur_ids = self.search(args, limit=limit)
        return cuur_ids.name_get()