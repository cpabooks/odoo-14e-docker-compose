# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
from datetime import date


class reportFreightInvoice(models.AbstractModel):
    _name = 'report.freight.report_freight_invoice'
    _description = 'Print freight Invoice.'
    def _get_ports(self,ids):
        ports= {}
        records=self.env['account.move'].browse(ids)
        for rec in records:
            for line in rec.invoice_line_ids:
                ports["pol"]=line.port_of_loading
                ports["pod"]=line.port_of_delivery
                break
        return ports
    def _get_container_sizes(self,ids):
        containers= []
        records=self.env['account.move'].browse(ids)
        for rec in records:
            for line in rec.invoice_line_ids:
                if line.freight_container_size:
                    containers.append(line.freight_container_size)

        return containers

    @api.model
    def _get_report_values(self, docids, data=None):

        return {
            'doc_ids' : docids,
            'doc_model' : self.env['account.move'],
            'docs':self.env['account.move'].browse(docids),
            'ports':self._get_ports(docids),
            'containers':self._get_container_sizes(docids),
            'mainCompany':self.env.ref('base.main_company'),
            'billingCurrency': self.env.ref('base.main_company').currency_id,
            'USCurrency': self.env.ref('base.USD'),
        }
