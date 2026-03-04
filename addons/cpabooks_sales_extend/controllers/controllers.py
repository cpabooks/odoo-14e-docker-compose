# -*- coding: utf-8 -*-
# from odoo import http


# class CpabooksSalesExtend(http.Controller):
#     @http.route('/cpabooks_sales_extend/cpabooks_sales_extend/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/cpabooks_sales_extend/cpabooks_sales_extend/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('cpabooks_sales_extend.listing', {
#             'root': '/cpabooks_sales_extend/cpabooks_sales_extend',
#             'objects': http.request.env['cpabooks_sales_extend.cpabooks_sales_extend'].search([]),
#         })

#     @http.route('/cpabooks_sales_extend/cpabooks_sales_extend/objects/<model("cpabooks_sales_extend.cpabooks_sales_extend"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('cpabooks_sales_extend.object', {
#             'object': obj
#         })
