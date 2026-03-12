# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
from datetime import date


class reportFreightQuotation(models.AbstractModel):
    _name = 'report.freight_in_quotation.report_freight_quotation'
    _description = 'Print freight Quotation.'

    def get_container_types(self,docids):
        container_types=[]
        for line in self.env['sale.order'].browse(docids):
            for rec in line.order_line:
                for subLine in rec.freight_details:
                    for container_line in subLine.container_lines:
                        if not container_line.container_type in container_types:
                            container_types.append(container_line.container_type)
        return container_types

    def get_freight_datas(self,docids):
        freight_datas={}

        freight_datas['orders']=[]
        freight_datas['chargeTypes']=[]
        for order in self.env['sale.order'].browse(docids):
            freight_datas['orders'].append(order)
            data={}
            data['currency']={}
            data["orderLines"]=[]
            for line in order.order_line:
                if line.foreign_currency not in data['currency']:
                    data['currency'][line.foreign_currency]=line.foreign_currency.rate

                line_data=self.calculate_order_line(line.id)
                data[line]=line_data
                data["orderLines"].append(line)
                for charge in line_data['chargeTypes']:
                    if charge not in freight_datas['chargeTypes']:
                        freight_datas['chargeTypes'].append(charge)
            freight_datas[order]=data
        return freight_datas

    def get_used_currency(self,order,destination_charges,freight_datas):
        used_currency={}
        for key in freight_datas[order]["currency"]:
            used_currency[key]=self.convert_currency(key.id,self.env.ref('base.main_company').currency_id.id)
        for port in destination_charges[order]['ports']:
            for line in destination_charges[order][port]['ChargeLines']:
                used_currency[line.currency] = self.convert_currency(line.currency.id, self.env.ref('base.main_company').currency_id.id)
        return used_currency



    def calculate_order_line(self,order_line_id):
        freightOrderLine = {}
        freightOrderLine["containers"] = []
        orderLine=self.env["sale.order.line"].search([('id','=',order_line_id)])
        freightOrderLine["freightLines"]=[]
        freightOrderLine["chargeTypes"]=[]
        for freightLine in orderLine.freight_details:
            freightLineDetails=self.calculate_freight_order_line_details(freightLine.id)
            freightOrderLine["freightLines"].append(freightLine)
            freightOrderLine[freightLine]= freightLineDetails
            chargeType=freightLine.charge_heading.charge_type
            if chargeType not in freightOrderLine["chargeTypes"]:
                freightOrderLine["chargeTypes"].append(chargeType)
                freightOrderLine[chargeType]={}
            for container in freightLineDetails["containers"]:
                if container not in freightOrderLine["containers"] :
                    freightOrderLine["containers"].append(container)
                    freightOrderLine[container]=0
                if container not in freightOrderLine[chargeType].keys():
                    freightOrderLine[chargeType][container]=0
                freightOrderLine[container]=freightOrderLine[container]+freightLineDetails[container]
                freightOrderLine[chargeType][container]=freightOrderLine[chargeType][container]+freightLineDetails[container]
        return freightOrderLine

    def calculate_freight_order_line_details(self,details_id):
        freightOrderLineDetails={}
        freightOrderLineDetails["containers"]=[]
        details=self.env["freight.order.line.details"].search([('id','=',details_id)])
        for container_line in details.container_lines:
            if container_line.container_type not in freightOrderLineDetails["containers"]:
                freightOrderLineDetails["containers"].append(container_line.container_type)
                freightOrderLineDetails[container_line.container_type]=container_line.container_freight
        return freightOrderLineDetails

    def convert_currency(self,from_currency_id,to_currency_id,Date=date.today()):
        conversion_rate=self.env['res.currency'].browse(from_currency_id).rate/self.env['res.currency'].browse(to_currency_id).rate
        return conversion_rate

    def get_destination_charges(self,docids):
        orders={}
        orders['orders']=[]
        for order in self.env['sale.order'].browse(docids):
            if order not in orders['orders']:
                orders['orders'].append(order)
                orders[order]={}
                orders[order]["lines"]=[]
                orders[order]['ports']=[]

                for line in order.order_line:
                    if line not in orders[order]["lines"]:
                        orders[order]["lines"].append(line)
                        orders[order][line]={}
                    POD=line.port_of_delivery
                    if not POD in orders[order]['ports']:
                        orders[order]['ports'].append(line.port_of_delivery)
                        orders[order][POD]= {}
                        orders[order][POD]["ChargeLines"]= []
                        orders[order][POD]["containers"]= {}
                        portCharge=self.env["freight.destination.charges"].search([("port_id", '=', POD.id)])
                        for rec in portCharge:
                            orders[order][POD]["ChargeLines"].append(rec)
                        stateCharge=self.env["freight.destination.charges"].search([("port_id", '=', False),("state", '=', POD.state.id)])
                        for rec in stateCharge:
                            orders[order][POD]["ChargeLines"].append(rec)
                        countryCharge=self.env["freight.destination.charges"].search([("port_id", '=', False),("state", '=',False),("country", '=', POD.country.id)])
                        for rec in countryCharge:
                            orders[order][POD]["ChargeLines"].append(rec)
                        shipment_charge=0
                        shipment_charge_local=0
                        orders[order][POD]["containers"]={}
                        for rec in orders[order][POD]["ChargeLines"]:
                            if rec.rate_basis.name!="Container":
                                shipment_charge=shipment_charge+rec.charge
                                shipment_charge_local=shipment_charge_local+(rec.charge/ self.convert_currency(rec.currency.id,self.env.ref('base.main_company').currency_id.id))
                            else :
                                for container in rec.container_lines:
                                    if container.container_type not in orders[order][POD]["containers"]:
                                        orders[order][POD]["containers"][container.container_type]= {}
                                        orders[order][POD]["containers"][container.container_type]['charge_forign']=0
                                        orders[order][POD]["containers"][container.container_type]['charge_local']=0
                                    orders[order][POD]["containers"][container.container_type]['charge_forign']=orders[order][POD]["containers"][container.container_type]['charge_forign']+container.container_freight
                                    orders[order][POD]["containers"][container.container_type]['charge_local']=orders[order][POD]["containers"][container.container_type]['charge_local']\
                                                                                                               +(container.container_freight/ self.convert_currency(rec.currency.id,self.env.ref('base.main_company').currency_id.id))
                        orders[order][POD]['shipmentCharge']=shipment_charge
                        orders[order][POD]['shipmentCharge_local']=shipment_charge_local
                        # for rec in orders[order][POD]["containers"]:
                        #     orders[order][POD]["containers"][rec]=orders[order][POD]["containers"][rec]+shipment_charge


        return orders



    @api.model
    def _get_report_values(self, docids, data=None):

        return {
            'doc_ids' : docids,
            'doc_model' : self.env['sale.order'],
            'container_types' : self.get_container_types(docids),
            'default_currency' : self.env.ref('base.main_company').currency_id,
            'freight_datas' : self.get_freight_datas(docids),
            'destination_charge' : self.get_destination_charges(docids),
            'used_currency' : self.get_used_currency,
            'convert_currency' : self.convert_currency,
            'docs' : self.env['sale.order'].browse(docids),
        }
