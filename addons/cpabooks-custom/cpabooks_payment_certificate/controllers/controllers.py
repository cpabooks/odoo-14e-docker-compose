# -*- coding: utf-8 -*-
# from odoo import http


# class CpabooksPaymentCertificate(http.Controller):
#     @http.route('/cpabooks_payment_certificate/cpabooks_payment_certificate/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/cpabooks_payment_certificate/cpabooks_payment_certificate/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('cpabooks_payment_certificate.listing', {
#             'root': '/cpabooks_payment_certificate/cpabooks_payment_certificate',
#             'objects': http.request.env['cpabooks_payment_certificate.cpabooks_payment_certificate'].search([]),
#         })

#     @http.route('/cpabooks_payment_certificate/cpabooks_payment_certificate/objects/<model("cpabooks_payment_certificate.cpabooks_payment_certificate"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('cpabooks_payment_certificate.object', {
#             'object': obj
#         })
