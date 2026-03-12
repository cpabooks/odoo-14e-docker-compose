# -*- coding: utf-8 -*-
# from odoo import http


# class CustomerVendorCode(http.Controller):
#     @http.route('/customer_vendor_code/customer_vendor_code/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/customer_vendor_code/customer_vendor_code/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('customer_vendor_code.listing', {
#             'root': '/customer_vendor_code/customer_vendor_code',
#             'objects': http.request.env['customer_vendor_code.customer_vendor_code'].search([]),
#         })

#     @http.route('/customer_vendor_code/customer_vendor_code/objects/<model("customer_vendor_code.customer_vendor_code"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('customer_vendor_code.object', {
#             'object': obj
#         })
