# -*- coding: utf-8 -*-
# from odoo import http


# class CpabooksDedicatedAmg(http.Controller):
#     @http.route('/cpabooks_dedicated_amg/cpabooks_dedicated_amg/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/cpabooks_dedicated_amg/cpabooks_dedicated_amg/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('cpabooks_dedicated_amg.listing', {
#             'root': '/cpabooks_dedicated_amg/cpabooks_dedicated_amg',
#             'objects': http.request.env['cpabooks_dedicated_amg.cpabooks_dedicated_amg'].search([]),
#         })

#     @http.route('/cpabooks_dedicated_amg/cpabooks_dedicated_amg/objects/<model("cpabooks_dedicated_amg.cpabooks_dedicated_amg"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('cpabooks_dedicated_amg.object', {
#             'object': obj
#         })
