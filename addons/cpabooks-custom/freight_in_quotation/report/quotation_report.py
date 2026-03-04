# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
from datetime import date


class reportFreightQuotation(models.AbstractModel):
    _name = 'report.freight_in_quotation.report_freight_quotation'
    _description = 'Print freight Quotation.'
    def get_order_lines(self,order_id):
        lines=self.env['sale.order.line'].search([("order_id","=",order_id)])
        return lines
    def get_pol_pod_paires(self,order_id):
        pol_pod_paires=[]
        lines=self.get_order_lines(order_id.id)
        for line in lines:
            polpod=(line.port_of_loading,line.port_of_delivery)
            if polpod not in pol_pod_paires:
                pol_pod_paires.append(polpod)
        return pol_pod_paires

    def mainCarierChargeTotal(self,order_id,polpod,containers):
        total={}
        order=self.env['sale.order'].browse(order_id.id)
        lines=self.env['sale.order.line'].search([("order_id","=",order_id.id),("port_of_loading","=",polpod[0].id),("port_of_delivery","=",polpod[1].id)])
        billingCurrency=self.env.ref('base.main_company').currency_id #order.billing_currency
        for line in lines:
            if "etd" not in total.keys():
                total["etd"]=line.freight_etd
            if "validity" not in total.keys():
                total["validity"]=line.rate_validity
            if "containerType" not in total.keys():
                total["containerType"]=line.freight_container_type.name
            if line.product_id.charge_type.id==1: #1 for main carier charges
                for container in containers:
                    if line.foreign_currency==billingCurrency:
                        if container not in total.keys():
                            total[container]=line[container]
                        else:
                            total[container]=total[container]+line[container]
                    else:
                        if container not in total.keys():
                            total[container]=line.foreign_currency.compute(line[container],billingCurrency)
                        else:
                            total[container]=total[container]+ line.foreign_currency.compute(line[container],billingCurrency)
        return total

    def otherChargeTotal(self,order_id,polpod,containers):
        total={}
        order=self.env['sale.order'].browse(order_id.id)
        lines=self.env['sale.order.line'].search([("order_id","=",order_id.id),("port_of_loading","=",polpod[0].id),("port_of_delivery","=",polpod[1].id)])
        billingCurrency=self.env.ref('base.main_company').currency_id
        for line in lines:
            if line.product_id.charge_type.id==2: #2 for other charges
                for container in containers:
                    if line.foreign_currency==billingCurrency:
                        if container not in total.keys():
                            total[container]=line[container]
                        else:
                            total[container]=total[container]+line[container]
                    else:
                        if container not in total.keys():
                            total[container]=line.foreign_currency.compute(line[container],billingCurrency)
                        else:
                            total[container]=total[container]+ line.foreign_currency.compute(line[container],billingCurrency)
        return total

    def desitnationChargeTotal(self,order_id,port,containers):
        total={}
        order=self.env['sale.order'].browse(order_id.id)
        lines=self.env['sale.order.line'].search([("order_id","=",order_id.id),("port_of_delivery","=",port.id)])
        billingCurrency=self.env.ref('base.main_company').currency_id
        for line in lines:
            if line.product_id.charge_type.id==2: #1 for main carier charges
                for container in containers:
                    if line.foreign_currency==billingCurrency:
                        if container not in total.keys():
                            total[container]=line[container]
                        else:
                            total[container]=total[container]+line[container]
                    else:
                        if container not in total.keys():
                            total[container]=line.foreign_currency.compute(line[container],billingCurrency)
                        else:
                            total[container]=total[container]+ line.foreign_currency.compute(line[container],billingCurrency)
        return total


    def get_report_data(self,docids):
        reportData={}
        reportData['orders']=[]
        reportData['ports']=[]
        reportData['currency']={}
        # Todo set containers here
        reportData['containers']=["freight_20ge","freight_40ge","freight_40hc"]
        for order in self.env['sale.order'].browse(docids):
            if  order not in reportData['orders']:
                reportData['orders'].append(order)
                reportData[order]={}
                reportData[order]["lines"]=[]
                reportData[order]['destination'] = {}
                reportData[order]['localCurrency'] = self.env.ref('base.main_company').currency_id
            for line in self.env['sale.order.line'].search([("order_id","=",order.id)]):
                if line.product_id.id:
                    reportData[order]["lines"].append(line)
                    PolPod = (line.port_of_loading, line.port_of_delivery)
                    if PolPod not in reportData['ports']:
                        reportData['ports'].append(PolPod)
                        reportData[order][PolPod]={}
                        reportData[order][PolPod]["mainCharges"]={}
                        reportData[order][PolPod]["mainCharges"]['total']={}
                        reportData[order][PolPod]["mainCharges"]['lines']=[]
                        reportData[order][PolPod]["destinationCharges"]={}
                        reportData[order][PolPod]["destinationCharges"]['total']={}
                        reportData[order][PolPod]["destinationCharges"]['lines']=[]
                    if line.product_id.charge_type.id==1: # 1 for main carier Charges
                        ### defjine foreign curency here
                        if not 'forex' in reportData[order].keys():
                            reportData[order]['forex']=line.foreign_currency
                        if line not in reportData[order][PolPod]["mainCharges"]["lines"]:
                            reportData[order][PolPod]["mainCharges"]["lines"].append(line)
                        for container in reportData['containers']:
                            if container not in reportData[order][PolPod]["mainCharges"].keys():
                                if container in line.fields_get_keys():
                                    reportData[order][PolPod]["mainCharges"][container]=self.convert_currency(line.foreign_currency.id,reportData[order]['forex'].id)*line[container]

                            else:
                                if container in line.fields_get_keys():
                                    reportData[order][PolPod]["mainCharges"][container]=reportData[order][PolPod]["mainCharges"][container]+self.convert_currency(line.foreign_currency.id,reportData[order]['forex'].id)*line[container]
                            if container not in reportData[order][PolPod]["mainCharges"]['total'].keys():
                                reportData[order][PolPod]["mainCharges"]['total'][container]=reportData[order][PolPod]["mainCharges"][container]
                            else:
                                reportData[order][PolPod]["mainCharges"]['total'][container]=reportData[order][PolPod]["mainCharges"]['total'][container]+reportData[order][PolPod]["mainCharges"][container]
                    else:
                        if line.port_of_delivery not in reportData[order]['destination'].keys():
                            ### defjine foreign curency here
                            reportData[order]['destination'][line.port_of_delivery]=[line]
                        else:
                            reportData[order]['destination'][line.port_of_delivery].append(line)

                        if line not in reportData[order][PolPod]["destinationCharges"]["lines"]:
                            reportData[order][PolPod]["destinationCharges"]["lines"].append(line)
                        for container in reportData['containers']:
                            if container not in reportData[order][PolPod]["destinationCharges"].keys():
                                if container in line.fields_get_keys():
                                    reportData[order][PolPod]["destinationCharges"][container]=self.convert_currency(line.foreign_currency.id,reportData[order]['localCurrency'].id)*line[container]
                            else:
                                if container in line.fields_get_keys():
                                    reportData[order][PolPod]["destinationCharges"][container]=reportData[order][PolPod]["destinationCharges"][container]+self.convert_currency(line.foreign_currency.id,reportData[order]['localCurrency'].id)*line[container]
                            if container not in reportData[order][PolPod]["destinationCharges"]['total'].keys():
                                reportData[order][PolPod]["destinationCharges"]['total'][container]=reportData[order][PolPod]["destinationCharges"][container]
                            else:
                                reportData[order][PolPod]["destinationCharges"]['total'][container]=reportData[order][PolPod]["destinationCharges"]['total'][container]+reportData[order][PolPod]["destinationCharges"][container]

            if line.foreign_currency not in reportData['currency']:
                reportData['currency'][line.foreign_currency] = line.foreign_currency.rate
        return reportData


    def convert_currency(self,from_currency_id,to_currency_id,Date=date.today()):
        conversion_rate=self.env['res.currency'].browse(from_currency_id).rate/self.env['res.currency'].browse(to_currency_id).rate
        return conversion_rate





    @api.model
    def _get_report_values(self, docids, data=None):

        return {
            'doc_ids' : docids,
            'doc_model' : self.env['sale.order'],
            'default_currency' : self.env.ref('base.main_company').currency_id,
            'convert_currency' : self.convert_currency,
            'reportData': self.get_report_data(docids),
            'docs' : self.env['sale.order'].browse(docids),
            'mainchargeTotal':self.mainCarierChargeTotal,
            'otherChargeTotal':self.otherChargeTotal,
            'desitnationChargeTotal':self.desitnationChargeTotal,
            'billingCurrency':self.env.ref('base.main_company').currency_id,
        }
