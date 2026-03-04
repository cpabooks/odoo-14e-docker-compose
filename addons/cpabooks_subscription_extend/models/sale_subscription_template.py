from odoo import api, models, fields, _
import logging

_logger = logging.getLogger(__name__)

class SaleSubscriptionTemplate(models.Model):
    _inherit = 'sale.subscription.template'


    @api.model
    def create_default_templates(self):
        """Create default template for Quarter Subscription"""
        templates = {
            'quarter' : {
                'name': 'Quarterly Subscription',
                'code': 'QUA',
                'user_closable': True,
                'recurring_interval': 3,
                'recurring_rule_type': 'monthly',
                'recurring_rule_boundary': 'limited',
                'recurring_rule_count': 6,
                'payment_mode': 'draft_invoice',
            },
            'year': {
                'name': 'Yearly Subscription',
                'code': 'YEA',
                'user_closable': True,
                'recurring_interval': 1,
                'recurring_rule_type': 'yearly',
                'recurring_rule_boundary': 'limited',
                'recurring_rule_count': 2,
                'payment_mode': 'draft_invoice',
            },
        }
        for key, vals in templates.items():
            search_val = self.search([
                ('code', '=', vals.get('code'))
            ], limit=1)
            if not search_val:
                self.create(vals)
                _logger.info(f"Sale Subscription Template created successfully {vals.get('name')}")
            else:
                search_val.write(vals)
                _logger.info(f"{vals.get('name')} template already exists")

