# -*- coding: utf-8 -*-
# from odoo import http


# class CpabooksPaymentVoucherStandard(http.Controller):
#     @http.route('/cpabooks_payment_voucher_standard/cpabooks_payment_voucher_standard/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/cpabooks_payment_voucher_standard/cpabooks_payment_voucher_standard/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('cpabooks_payment_voucher_standard.listing', {
#             'root': '/cpabooks_payment_voucher_standard/cpabooks_payment_voucher_standard',
#             'objects': http.request.env['cpabooks_payment_voucher_standard.cpabooks_payment_voucher_standard'].search([]),
#         })

#     @http.route('/cpabooks_payment_voucher_standard/cpabooks_payment_voucher_standard/objects/<model("cpabooks_payment_voucher_standard.cpabooks_payment_voucher_standard"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('cpabooks_payment_voucher_standard.object', {
#             'object': obj
#         })
