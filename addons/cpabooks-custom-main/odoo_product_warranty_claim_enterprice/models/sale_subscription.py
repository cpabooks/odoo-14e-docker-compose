# -*- coding: utf-8 -*-
import datetime
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models


class SaleSubscription(models.Model):
    _inherit = "sale.subscription"

    custom_customer_warranty_count = fields.Integer(
        compute='_customer_warranty_count_enterprice'
    )

    def _customer_warranty_count_enterprice(self):
        """Compute the number of distinct warranty linked to the order."""
        for rec in self:
            warranty_count = self.env['product.warranty.registration'].search_count([
                ('subscription_id', '=', rec.id)
            ])
            rec.custom_customer_warranty_count = warranty_count or 0

    def action_customer_warrantys(self):
        """Display the linked warranty and adapt the view to the number of records to display."""
        self.ensure_one()
        warranty_count_ids = self.env['product.warranty.registration'].search([
            ('subscription_id', '=', self.id)
        ])
        action = self.env.ref('odoo_product_warranty_claim_enterprice.action_product_warranty_claim_custom').read()[0]
        action['domain'] = [('id', 'in', warranty_count_ids.ids)]
        return action
