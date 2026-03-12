# -*- coding: utf-8 -*-
import datetime
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    custom_customer_warranty_count = fields.Integer(
        compute='_customer_warranty_count_enterprice'
    )

    def _customer_warranty_count_enterprice(self):
        """Compute the number of distinct warranty linked to the order."""
        for rec in self:
            warranty_count = self.env['product.warranty.registration'].search_count([
                ('sale_order_id', '=', rec.id)
            ])
            rec.custom_customer_warranty_count = warranty_count or 0

    def action_customer_warrantys(self):
        """Display the linked warranty and adapt the view to the number of records to display."""
        self.ensure_one()
        warranty_count_ids = self.env['product.warranty.registration'].search([
            ('sale_order_id', '=', self.id)
        ])
        action = self.env.ref('odoo_product_warranty_claim_enterprice.action_product_warranty_claim_custom').read()[0]
        action['domain'] = [('id', 'in', warranty_count_ids.ids)]
        return action

    # @api.multi
    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        for rec in self:
            for line in rec.order_line:
                if line.product_id.custom_allow_warranty:
                    values = {
                        'recurring_rule_type': line.product_id.custom_warranty_rule_type,
                        'recurring_interval': line.product_id.custom_warranty_interval,
                    }
                    today = datetime.date.today()
                    periods = {'daily': 'days', 'weekly': 'weeks', 'monthly': 'months', 'yearly': 'years'}
                    invoicing_period = relativedelta(**{periods[values['recurring_rule_type']]: values['recurring_interval']})
                    recurring_next_date = today + invoicing_period
                    prevday = recurring_next_date - datetime.timedelta(days=1)
                    warranty_vals = {
                        #'name': self.env['ir.sequence'].next_by_code('product.warranty.seq'),
                        'product_id': line.product_id.id,
                        'uom_id': line.product_id.uom_id.id,
                        'quantity': line.product_uom_qty,
                        'start_date': fields.Date.today(),
                        'end_date': prevday,
                        'contract_id': rec.analytic_account_id.id,
                        'sale_order_id':line.order_id.id,
                        'partner_id':line.order_id.partner_id.id,
                        'state': 'confirm',
                        'active': True
                    }
                    if line.product_id.recurring_invoice:
                        warranty_vals.update({
                            'subscription_id': line.subscription_id.id
                        })
                    warranty_product = self.env['product.warranty.registration'].create(warranty_vals)
        return res

    # @api.multi
    def unlink(self):
        for order in self:
            warranty_id = self.env['product.warranty.registration'].search([
                ('sale_order_id', '=', order.id)
            ])
            if warranty_id:
                warranty_id.write({'active': False})
        return super(SaleOrder, self).unlink()

    # @api.multi
    def action_cancel(self):
        for order in self:
            warranty_id = self.env['product.warranty.registration'].search([
                ('sale_order_id', '=', order.id)
            ])
            if warranty_id:
                warranty_id.write({'active': False})
        return super(SaleOrder, self).action_cancel()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
