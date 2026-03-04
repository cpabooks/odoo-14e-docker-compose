import time

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class SaleAdvancePaymentInvInherit(models.TransientModel):
    _inherit = "sale.advance.payment.inv"

    def _get_advance_details(self, order):
        if self.advance_payment_method == 'percentage':
            # amount = (order.total_after_discount if order.total_after_discount>0 else order.amount_untaxed) * self.amount / 100
            amount = order.amount_total * self.amount / 100
            name = _("Down payment of %s%%") % (self.amount)
        else:
            amount = self.fixed_amount
            name = _('Down Payment')

        return amount, name