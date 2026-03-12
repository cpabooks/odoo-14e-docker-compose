from odoo import api, models, fields, _
import logging

_logger = logging.getLogger(__name__)

class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.model
    def create_products_for_subscriptions(self):
        """Create default products for subscription"""
        products = {
            'quarter': {
                'name': 'Quarterly Services',
                'sale_ok': True,
                'purchase_ok': True,
                'type': 'service',  # 🔹 Fixed 'product_type' -> 'type'
                'lst_price': 1.00,
                'company_id': self.env.company.id,
            },
            'month': {
                'name': 'Monthly Services',
                'sale_ok': True,
                'purchase_ok': True,
                'type': 'service',  # 🔹 Fixed 'product_type' -> 'type'
                'lst_price': 1.00,
                'company_id': self.env.company.id,
            },
            'year': {
                'name': 'Yearly Services',
                'sale_ok': True,
                'purchase_ok': True,
                'type': 'service',  # 🔹 Fixed 'product_type' -> 'type'
                'lst_price': 1.00,
                'company_id': self.env.company.id,
            }
        }

        for key, vals in products.items():
            search_val = self.search([('name', '=', vals.get('name'))], limit=1)
            if not search_val:
                self.create(vals)
                _logger.info(f"Subscription products created successfully. {vals.get('name')}")

            else:
                search_val.write(vals)
                _logger.info(f"{vals.get('name')} product already exists")
