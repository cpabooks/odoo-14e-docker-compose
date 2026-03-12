# -*- coding: utf-8 -*-

from odoo import models, fields, api


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    vendor_code = fields.Char(string="Vendor Code")

    @api.onchange('partner_id')
    def _onchange_purchase_partner(self):
        for i in self:
            if i.partner_id:
                i.vendor_code = i.partner_id.ref


    # def action_view_invoice(self):
    #     ks_res = super(PurchaseOrder, self).action_view_invoice()
    #     for rec in self:
    #         ks_res['partner_code'] = rec.vendor_code
    #     return ks_res

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    customer_code = fields.Char(string="Customer Code")

    @api.onchange('partner_id')
    def _onchange_sale_partner(self):
        for i in self:
            if i.partner_id:
                i.customer_code = i.partner_id.ref

    def _prepare_invoice(self):
        invoice_vals = super(SaleOrder, self)._prepare_invoice()

        if self.customer_code:
            invoice_vals['partner_code'] = self.customer_code
        return invoice_vals

class AccountMove(models.Model):
    _inherit = "account.move"

    partner_code = fields.Char(string="Partner Code")

    @api.onchange('partner_id')
    def _onchange_account_partner(self):
        for i in self:
            if i.partner_id:
                i.partner_code = i.partner_id.ref

    @api.onchange("purchase_vendor_bill_id", "purchase_id")
    def _onchange_purchase_auto_complete(self):
        """
        Override to add Operating Unit from Purchase Order to Invoice.
        """
        purchase_id = self.purchase_id
        if self.purchase_vendor_bill_id.purchase_order_id:
            purchase_id = self.purchase_vendor_bill_id.purchase_order_id
        if purchase_id and purchase_id.vendor_code:
            # Assign OU from PO to Invoice
            self.partner_code = purchase_id.vendor_code
        return super()._onchange_purchase_auto_complete()