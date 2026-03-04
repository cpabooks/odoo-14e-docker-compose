# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def get_signature(self):
        get_signature_data=self.env['signature.setup'].search([('model','=','sale.order'),('company_id','=',self.env.company.id)])
        return  get_signature_data
