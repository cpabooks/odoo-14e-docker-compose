# -*- coding: utf-8 -*-
# from odoo import http


# class CpabooksDedicatedKcs(http.Controller):
#     @http.route('/cpabooks_dedicated_kcs/cpabooks_dedicated_kcs/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/cpabooks_dedicated_kcs/cpabooks_dedicated_kcs/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('cpabooks_dedicated_kcs.listing', {
#             'root': '/cpabooks_dedicated_kcs/cpabooks_dedicated_kcs',
#             'objects': http.request.env['cpabooks_dedicated_kcs.cpabooks_dedicated_kcs'].search([]),
#         })

#     @http.route('/cpabooks_dedicated_kcs/cpabooks_dedicated_kcs/objects/<model("cpabooks_dedicated_kcs.cpabooks_dedicated_kcs"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('cpabooks_dedicated_kcs.object', {
#             'object': obj
#         })
