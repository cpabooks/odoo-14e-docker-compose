# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    job_count=fields.Integer()


    def action_create_job(self):
        return True
    def action_view_job(self):
        return True
