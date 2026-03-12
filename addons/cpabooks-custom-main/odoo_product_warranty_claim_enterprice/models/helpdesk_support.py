# -*- coding: utf-8 -*-

from odoo import models, fields, api


class HelpdeskSupport(models.Model):
    _inherit = 'helpdesk.ticket'
    
    custom_warranty_number = fields.Char(
        string='Warranty Number',
        copy=True
    )
    custom_contract_reference = fields.Char(
        string='SO / Contract Reference',
        copy=True,
    )
    custom_serial_number = fields.Char(
        'Serial Number',
        copy=True,
    )
    custom_warranty_start_date = fields.Date(
        'Warranty Start Date',
        copy=True,
    )
    custom_warranty_end_date = fields.Date(
        'Warranty End Date',
        copy=True,
    )
    custom_warranty_id = fields.Many2one(
        'product.warranty.registration',
        strong='Warranty',
    )
    
    custom_is_claim = fields.Boolean(
        string='Is Claim ?',
        default=False,
    )
    custom_phone = fields.Char(
        string='Phone'
    )
    custom_category = fields.Selection(
        [('technical','Technical'),
         ('functional','Functional'),
         ('support','Support'),
        ],
        string='Category',
    )

    @api.onchange('custom_warranty_id')
    def onchange_custom_warranty(self):
        for ticket in self:
            ticket.custom_warranty_number = self.custom_warranty_id.name
            ticket.custom_serial_number = self.custom_warranty_id.serial_number
            ticket.custom_warranty_start_date = self.custom_warranty_id.start_date
            ticket.custom_warranty_end_date = self.custom_warranty_id.end_date

    # @api.multi
    def action_show_warranty_product(self):
        self.ensure_one()
        res = self.env.ref('odoo_product_warranty_claim_enterprice.action_product_warranty_claim_custom')
        res = res.read()[0]
        res['domain'] = str([('id','=',self.custom_warranty_id.id)])
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
