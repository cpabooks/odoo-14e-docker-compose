# -*- coding: utf-8 -*-
# from odoo import http


# class CpabooksDedicatedSamurai(http.Controller):
#     @http.route('/cpabooks_dedicated_samurai/cpabooks_dedicated_samurai/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/cpabooks_dedicated_samurai/cpabooks_dedicated_samurai/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('cpabooks_dedicated_samurai.listing', {
#             'root': '/cpabooks_dedicated_samurai/cpabooks_dedicated_samurai',
#             'objects': http.request.env['cpabooks_dedicated_samurai.cpabooks_dedicated_samurai'].search([]),
#         })

#     @http.route('/cpabooks_dedicated_samurai/cpabooks_dedicated_samurai/objects/<model("cpabooks_dedicated_samurai.cpabooks_dedicated_samurai"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('cpabooks_dedicated_samurai.object', {
#             'object': obj
#         })
