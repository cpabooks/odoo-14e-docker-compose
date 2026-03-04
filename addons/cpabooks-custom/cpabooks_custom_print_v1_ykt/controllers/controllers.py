# -*- coding: utf-8 -*-
# from odoo import http


# class CpabooksCustomPrintV1Ykt(http.Controller):
#     @http.route('/cpabooks_custom__print_v1_ykt/cpabooks_custom__print_v1_ykt/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/cpabooks_custom__print_v1_ykt/cpabooks_custom__print_v1_ykt/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('cpabooks_custom__print_v1_ykt.listing', {
#             'root': '/cpabooks_custom__print_v1_ykt/cpabooks_custom__print_v1_ykt',
#             'objects': http.request.env['cpabooks_custom__print_v1_ykt.cpabooks_custom__print_v1_ykt'].search([]),
#         })

#     @http.route('/cpabooks_custom__print_v1_ykt/cpabooks_custom__print_v1_ykt/objects/<model("cpabooks_custom__print_v1_ykt.cpabooks_custom__print_v1_ykt"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('cpabooks_custom__print_v1_ykt.object', {
#             'object': obj
#         })
