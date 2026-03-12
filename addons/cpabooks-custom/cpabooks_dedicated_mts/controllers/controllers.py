# -*- coding: utf-8 -*-
# from odoo import http


# class CpabooksDedicatedMts(http.Controller):
#     @http.route('/cpabooks_dedicated_mts/cpabooks_dedicated_mts/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/cpabooks_dedicated_mts/cpabooks_dedicated_mts/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('cpabooks_dedicated_mts.listing', {
#             'root': '/cpabooks_dedicated_mts/cpabooks_dedicated_mts',
#             'objects': http.request.env['cpabooks_dedicated_mts.cpabooks_dedicated_mts'].search([]),
#         })

#     @http.route('/cpabooks_dedicated_mts/cpabooks_dedicated_mts/objects/<model("cpabooks_dedicated_mts.cpabooks_dedicated_mts"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('cpabooks_dedicated_mts.object', {
#             'object': obj
#         })
