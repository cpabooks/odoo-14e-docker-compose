# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by Candidroot Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.
from odoo import models,api,fields,_


class ResCompany(models.Model):
    
    _inherit = 'res.company'
    
    
    account_aged_receivable_auto_reconcile = fields.Boolean(string='Enable Auto Reconcile on Aged Receivable')
    account_aged_payable_auto_reconcile = fields.Boolean(string='Enable Auto Reconcile on Aged Payable')
    account_partner_ledger_auto_reconcile = fields.Boolean(string='Enable Auto Reconcile on Partner Ledger')
    
    
    