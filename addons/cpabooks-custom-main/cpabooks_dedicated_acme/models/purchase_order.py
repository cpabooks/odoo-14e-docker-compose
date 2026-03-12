
from odoo import fields, models,api, _
from odoo.exceptions import ValidationError


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    @api.onchange('product_id')
    def product_id_change(self):
        if not self.product_id:
            return
        test = self.order_id.order_line.filtered(
            lambda x: x.product_id.id == self.product_id.id and x.product_template_id)
        new_test=test[0:-1]
        if len(new_test) > 1:
            raise ValidationError(_("This product is already added in purchase order line"))

