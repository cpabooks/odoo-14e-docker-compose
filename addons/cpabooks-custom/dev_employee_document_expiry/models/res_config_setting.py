# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://www.devintellecs.com>).
#
#    For Module Support : devintelle@gmail.com  or Skype : devintelle
#
##############################################################################

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'


    expiry_before_days = fields.Integer(string="Before Days",default=1)

    @api.onchange('expiry_before_days')
    def _check_days(self):
        if self.expiry_before_days:
            if self.expiry_before_days <= 0:
                raise ValidationError("Before Days must be greater than 0")

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        ir_param = self.env['ir.config_parameter']
        ir_param.sudo().set_param("dev_employee_document_expiry.expiry_before_days",
                                      self.expiry_before_days)

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        params = self.env['ir.config_parameter'].sudo()
        res.update(expiry_before_days=
                   int(params.get_param("dev_employee_document_expiry.expiry_before_days",
                                        default=False)) or False)

        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
