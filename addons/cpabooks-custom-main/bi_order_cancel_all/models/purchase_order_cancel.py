# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import models, api

class purchase(models.Model):
    _inherit = 'purchase.order'

    
    def button_cancel(self):
        """
        Cancel order,invoice and picking
        """
        if self.picking_ids:
            self.picking_ids.action_cancel()
        if self.invoice_ids:
            self.invoice_ids.button_cancel()
        return super(purchase, self).button_cancel()

