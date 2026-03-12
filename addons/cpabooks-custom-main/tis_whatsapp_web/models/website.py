# -*- coding: utf-8 -*-
# This module and its content is copyright of Technaureus Info Solutions Pvt. Ltd.
# - © Technaureus Info Solutions Pvt. Ltd 2020. All rights reserved.

from odoo import models, fields


class Website(models.Model):
    _inherit = "website"

    whatsapp_no = fields.Char('Whatsapp Number')

    def get_url(self, whatsapp_no):
        return 'https://web.whatsapp.com/send?phone=' + whatsapp_no

    def get_api_url(self, whatsapp_no):
        return 'https://api.whatsapp.com/send?phone=' + whatsapp_no
