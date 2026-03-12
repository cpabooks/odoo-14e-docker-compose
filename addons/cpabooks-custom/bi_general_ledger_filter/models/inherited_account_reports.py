# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import models, api, fields, _

class AccountReports(models.AbstractModel):
    _inherit = 'account.report'


    filter_custom_account = None
    filter_custom_account_type = None

    @api.model
    def _init_filter_custom_account(self, options, previous_options=None):
        if not self.filter_custom_account:
            return
        options['custom_account'] = True
        options['custom_account_ids'] = previous_options and previous_options.get('custom_account_ids') or []
        selected_custom_account_ids = [int(account) for account in options['custom_account_ids']]
        selected_custom_accountes = selected_custom_account_ids and self.env['account.account'].browse(selected_custom_account_ids) or self.env['account.account']
        options['selected_custom_account_ids'] = selected_custom_accountes.mapped('name')
        return options


    @api.model
    def _init_filter_custom_account_type(self, options, previous_options=None):
        if not self.filter_custom_account_type:
            return

        options['custom_account_type'] = True
        options['custom_account_type_ids'] = previous_options and previous_options.get('custom_account_type_ids') or []
        selected_custom_account_type_ids = [int(account_type) for account_type in options['custom_account_type_ids']]
        selected_custom_account_typees = selected_custom_account_type_ids and self.env['account.account.type'].browse(selected_custom_account_type_ids) or self.env['account.account.type']
        options['selected_custom_account_type_ids'] = selected_custom_account_typees.mapped('name')
        return options

    @api.model
    def _get_options(self, previous_options=None):
        # OVERRIDE
        options = super(AccountReports, self)._get_options(previous_options=previous_options)
        self._init_filter_custom_account(options, previous_options)
        self._init_filter_custom_account_type(options, previous_options)
        return options

    
    def _set_context(self, options):
        ctx = super(AccountReports, self)._set_context(options)
        if options.get('custom_account_ids'):
            ctx['custom_account_ids'] = self.env['account.account'].browse([int(account) for account in options.get('custom_account_ids',[])])

        if options.get('custom_account_type_ids'):
            ctx['custom_account_type_ids'] = self.env['account.account.type'].browse([int(account) for account in options.get('custom_account_type_ids',[])])            
        return ctx


    def get_report_informations(self, options):
        '''
        return a dictionary of informations that will be needed by the js widget, manager_id, footnotes, html of report and searchview, ...
        '''
        info = super(AccountReports, self).get_report_informations(options)
        if options and options.get('custom_account_type'):
            info['selected_custom_account_type_ids'] = [self.env['account.account.type'].browse(int(account)).name for account in options.get('custom_account_type_ids',[])]

        if options and options.get('custom_account'):
            info['selected_custom_account_ids'] = [self.env['account.account'].browse(int(account)).name for account in options.get('custom_account_ids',[])]    

        return info