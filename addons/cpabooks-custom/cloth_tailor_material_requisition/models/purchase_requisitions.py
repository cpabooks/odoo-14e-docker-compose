# -*- coding: utf-8 -*-

from odoo import models, fields , api


class MaterialPurchaseRequisition(models.Model):
    _inherit = "material.purchase.requisition"

    custom_cloth_request_id = fields.Many2one(
        'cloth.request.details',
        string='Cloth Request',
        readonly=False,
        copy=False,
    )
    custom_workorder_request_id = fields.Many2one(
        'project.task',
        string='Workorder Request',
        readonly=False,
        copy=False,
    )
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
