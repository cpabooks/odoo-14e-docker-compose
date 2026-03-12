# -*- coding: utf-8 -*-
# from odoo import http


# class CpabooksDedicatedGp(http.Controller):
#     @http.route('/cpabooks_dedicated_gp/cpabooks_dedicated_gp/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/cpabooks_dedicated_gp/cpabooks_dedicated_gp/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('cpabooks_dedicated_gp.listing', {
#             'root': '/cpabooks_dedicated_gp/cpabooks_dedicated_gp',
#             'objects': http.request.env['cpabooks_dedicated_gp.cpabooks_dedicated_gp'].search([]),
#         })

#     @http.route('/cpabooks_dedicated_gp/cpabooks_dedicated_gp/objects/<model("cpabooks_dedicated_gp.cpabooks_dedicated_gp"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('cpabooks_dedicated_gp.object', {
#             'object': obj
#         })
