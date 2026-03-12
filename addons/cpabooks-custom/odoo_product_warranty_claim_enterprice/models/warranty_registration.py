# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ProductWarrantyRegistration(models.Model):
    _name = 'product.warranty.registration'
    _descritpion = "Warranty"
    _rec_name = 'name'
    _order = 'name desc'
    _inherit = ['mail.thread', 'mail.activity.mixin','portal.mixin']

    @api.model
    def create(self, vals):
        number = self.env['ir.sequence'].next_by_code('product.warranty.seq')
        vals.update({
            'name': number,
        })
        return super(ProductWarrantyRegistration, self).create(vals)
    
    name = fields.Char(
        string='Number',
        copy=False,
    )
    serial_number = fields.Char(
        string='Serial Number',
        copy=False,
    )
    sale_order_id = fields.Many2one(
        'sale.order',
        copy=False,
    )
    partner_id = fields.Many2one(
        'res.partner',
        string='Customer',
        copy=True,
        required=True,
    )
    product_id = fields.Many2one(
        'product.product',
        string='Customer Warranty',
        copy=True,
        required=True,
    )
    uom_id = fields.Many2one(
        'uom.uom',
        string='Unit of Measure',
        copy=True,
    )
    quantity = fields.Float(
        string='Quantity',
        copy=True,
    )
    contract_id = fields.Many2one(
        'account.analytic.account',
        string='Analytic Account',
        copy=True,
    )
    start_date = fields.Date(
        string='Warranty Start Date',
        copy=True,
    )
    end_date = fields.Date(
        string='Warranty End Date',
        copy=True,
    )
    helpdesk_support_ids = fields.One2many(
        'helpdesk.ticket',
        'custom_warranty_id',
         string='Helpdesk Support',
    )
    state = fields.Selection(
        [('draft','Draft'),
         ('confirm','Confirmed'),
         ('cancel','Cancelled'),
         ('done','Done')],
        string='State',
        default='draft',
        track_visibility='onchange',
    )
    user_id = fields.Many2one(
        'res.users',
        string='User',
        default=lambda self: self.env.user,
        readonly=True,
    )
    company_id = fields.Many2one(
        'res.company',
        default=lambda self: self.env.user.company_id, 
        string='Company',
        readonly=True,
    )
    custom_date = fields.Date(
        default=fields.date.today(),
        string='Create Date',
        readonly=True,
    )
    notes = fields.Text(
        string='Notes',
    )
    subscription_id = fields.Many2one(
        'sale.subscription',
        'Subscription',
        copy=False
    )
    active = fields.Boolean(
        string="Active",
        default=True
    )

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
