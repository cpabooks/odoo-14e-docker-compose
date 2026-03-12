# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by Candidroot Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.

from odoo import models,api,fields,_



class ResConfigSettings(models.TransientModel):
    
    _inherit = 'res.config.settings'
    
    
    aged_receivable_auto_reconcile = fields.Boolean(string='Enable Auto Reconcile on Aged Receivable',related='company_id.account_aged_receivable_auto_reconcile', readonly=False)
    aged_payable_auto_reconcile = fields.Boolean(string='Enable Auto Reconcile on Aged Payable',related='company_id.account_aged_payable_auto_reconcile', readonly=False)
    partner_ledger_auto_reconcile = fields.Boolean(string='Enable Auto Reconcile on Partner Ledger',related='company_id.account_partner_ledger_auto_reconcile', readonly=False)
    
    
    