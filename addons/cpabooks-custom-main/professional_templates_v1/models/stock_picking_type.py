from odoo import models, fields, api, _


class stockPickingType(models.Model):
    _inherit = 'stock.picking.type'

    def create(self,vals):
        res=super(stockPickingType, self).create(vals)
        for rec in res:
            rec.show_operations=False

        return res
