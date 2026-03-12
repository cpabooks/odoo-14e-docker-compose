# -*- coding: utf-8 -*-
# from odoo import http


# class CpabooksSaleDiscountWithTaxPt(http.Controller):
#     @http.route('/cpabooks_sale_discount_with_tax_pt/cpabooks_sale_discount_with_tax_pt/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/cpabooks_sale_discount_with_tax_pt/cpabooks_sale_discount_with_tax_pt/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('cpabooks_sale_discount_with_tax_pt.listing', {
#             'root': '/cpabooks_sale_discount_with_tax_pt/cpabooks_sale_discount_with_tax_pt',
#             'objects': http.request.env['cpabooks_sale_discount_with_tax_pt.cpabooks_sale_discount_with_tax_pt'].search([]),
#         })

#     @http.route('/cpabooks_sale_discount_with_tax_pt/cpabooks_sale_discount_with_tax_pt/objects/<model("cpabooks_sale_discount_with_tax_pt.cpabooks_sale_discount_with_tax_pt"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('cpabooks_sale_discount_with_tax_pt.object', {
#             'object': obj
#         })
