# -*- coding: utf-8 -*-
###############################################################################
#
#    Fortutech IMS Pvt. Ltd.
#    Copyright (C) 2016-TODAY Fortutech IMS Pvt. Ltd.(<http://www.fortutechims.com>).
#
###############################################################################
from odoo import models, fields, api, _


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def get_parameter_value(self):
        res_confirm_order = self.env['ir.config_parameter'].sudo().get_param('fims_sale_automatic_workflow.web_order_conf')
        res = {}
        if res_confirm_order == 'conf_quo':
            res.update({'1':'conf_quo'})
            return 'conf_quo'

        if res_confirm_order == 'conf_quo_and_inv':
            res.update({'2':'conf_quo_and_inv'})
            return 'conf_quo_and_inv'

        if res_confirm_order == 'conf_quo_and_validate_inv':
            res.update({'3':'conf_quo_and_validate_inv'})
            return 'conf_quo_and_validate_inv'

        if res_confirm_order == 'conf_quo_inv_payment':
            res.update({'4':'conf_quo_inv_payment'})
            return 'conf_quo_inv_payment'

    def sale_auto_payment_fims(self):
        res_confirm_order = self.env['ir.config_parameter'].sudo().get_param(
            'fims_sale_automatic_workflow.web_order_conf')

        if res_confirm_order == 'conf_quo':
            for sale in self:
                sale.action_confirm()

        if res_confirm_order == 'conf_quo_and_inv':
            for sale in self:
                sale.action_confirm()

                invoice_wiz = self.env['sale.advance.payment.inv'].create({
                    'advance_payment_method': 'delivered',
                })
                inv_ids = invoice_wiz.with_context(active_ids=sale.ids).create_invoices()

        if res_confirm_order == 'conf_quo_and_validate_inv':
            for sale in self:
                sale.action_confirm()
                invoice_wiz = self.env['sale.advance.payment.inv'].create({
                    'advance_payment_method': 'delivered',
                })
                invoices = sale._create_invoices()
                invoices.action_post()

        if res_confirm_order == 'conf_quo_inv_payment':
            for sale in self:
                sale.action_confirm()
                invoice_wiz = self.env['sale.advance.payment.inv'].create({
                    'advance_payment_method': 'delivered',
                })
                invoices = sale._create_invoices()
                invoices.action_post()
                today = fields.Date.today()
                self.env['account.payment.register'].with_context(active_ids=invoices.ids,
                                                                  active_model='account.move').create({
                    'payment_date': today,
                })._create_payments()

                default_template = self.env['ir.config_parameter'].sudo().get_param('sale.default_email_template')
                if default_template:
                    for trans in self:
                        ctx_company = {'company_id': trans.company_id.id,
                                       'force_company': trans.company_id.id,
                                       'mark_invoice_as_sent': True,
                                       }
                        trans = trans.with_context(ctx_company)
                        for invoice in invoices:
                            try:
                                invoice.message_post_with_template(int(default_template),
                                                                   email_layout_xmlid="mail.mail_notification_paynow")
                            except:
                                pass
