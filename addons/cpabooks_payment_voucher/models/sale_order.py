from odoo import api, fields, models, _


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    payment_count = fields.Integer(string='Payment Count', compute="_compute_payment_count")

    def _get_linked_payments(self):
        """
        Helper method to find all unique account.payment records
        reconciled with invoices related to this Sale Order.
        """
        self.ensure_one()
        # Look for partial reconciliations on those lines
        # 'matched_debit_ids' and 'matched_credit_ids' link invoices to payments
        payments = self.env['account.payment'].search([('so_id', '=', self.id),('state', '=', 'posted')])  # Start with all posted payments

        # Filter out empty records (in case some reconciliations aren't linked to a payment object)
        return payments

    def _compute_payment_count(self):
        for order in self:
            order.payment_count = len(order._get_linked_payments())

    def action_view_relavent_payment(self):
        self.ensure_one()
        payments = self._get_linked_payments()

        action = {
            'name': _('Payments'),
            'type': 'ir.actions.act_window',
            'res_model': 'account.payment',
            'context': {'create': False},
        }

        if len(payments) == 1:
            # If only one payment, go straight to the form view
            action.update({
                'view_mode': 'form',
                'res_id': payments.id,
            })
        else:
            # If multiple payments, show the list (tree) view
            action.update({
                'view_mode': 'tree,form',
                'domain': [('id', 'in', payments.ids)],
            })
        return action