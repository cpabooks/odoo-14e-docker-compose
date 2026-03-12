# -*- coding: utf-8 -*-
# from odoo import http


# class CpabooksDedicatedWc(http.Controller):
#     @http.route('/cpabooks_dedicated_wc/cpabooks_dedicated_wc/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/cpabooks_dedicated_wc/cpabooks_dedicated_wc/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('cpabooks_dedicated_wc.listing', {
#             'root': '/cpabooks_dedicated_wc/cpabooks_dedicated_wc',
#             'objects': http.request.env['cpabooks_dedicated_wc.cpabooks_dedicated_wc'].search([]),
#         })

#     @http.route('/cpabooks_dedicated_wc/cpabooks_dedicated_wc/objects/<model("cpabooks_dedicated_wc.cpabooks_dedicated_wc"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('cpabooks_dedicated_wc.object', {
#             'object': obj
#         })
