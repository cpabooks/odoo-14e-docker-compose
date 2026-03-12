# -*- coding: utf-8 -*-
# from odoo import http


# class CpabooksDedicatedDiamondrose(http.Controller):
#     @http.route('/cpabooks_dedicated_diamondrose/cpabooks_dedicated_diamondrose/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/cpabooks_dedicated_diamondrose/cpabooks_dedicated_diamondrose/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('cpabooks_dedicated_diamondrose.listing', {
#             'root': '/cpabooks_dedicated_diamondrose/cpabooks_dedicated_diamondrose',
#             'objects': http.request.env['cpabooks_dedicated_diamondrose.cpabooks_dedicated_diamondrose'].search([]),
#         })

#     @http.route('/cpabooks_dedicated_diamondrose/cpabooks_dedicated_diamondrose/objects/<model("cpabooks_dedicated_diamondrose.cpabooks_dedicated_diamondrose"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('cpabooks_dedicated_diamondrose.object', {
#             'object': obj
#         })
