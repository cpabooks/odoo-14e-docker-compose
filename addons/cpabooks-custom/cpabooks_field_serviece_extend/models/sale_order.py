from odoo import api, models, fields, _


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.model
    def create(self, vals):
        # 1. Let Odoo create the Quotation record in the database first
        order = super(SaleOrder, self).create(vals)

        # 2. Check if this Quotation is linked to an FSM Task
        # In Odoo FSM, creating a quotation from a task automatically fills the 'task_id' field on the Sale Order
        if order.task_id:
            # Change the task stage to 'qty_issued' only because the quotation is now officially saved
            order.task_id.stage = 'qty_issued'

        return order

    def action_confirm(self):
        # 1. Let Odoo confirm the Sale Order first (state changes to 'sale')
        res = super(SaleOrder, self).action_confirm()

        # 2. Check if this confirmed order belongs to an FSM Task
        for order in self:
            if order.task_id:
                # Change the task stage to 'qty_approved' because the Quotation was confirmed
                order.task_id.stage = 'qty_approved'

        return res