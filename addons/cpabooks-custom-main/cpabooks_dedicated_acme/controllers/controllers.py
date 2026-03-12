# -*- coding: utf-8 -*-
# from odoo import http


# class CpabooksDedicatedAcme(http.Controller):
#     @http.route('/cpabooks_dedicated_acme/cpabooks_dedicated_acme/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/cpabooks_dedicated_acme/cpabooks_dedicated_acme/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('cpabooks_dedicated_acme.listing', {
#             'root': '/cpabooks_dedicated_acme/cpabooks_dedicated_acme',
#             'objects': http.request.env['cpabooks_dedicated_acme.cpabooks_dedicated_acme'].search([]),
#         })

#     @http.route('/cpabooks_dedicated_acme/cpabooks_dedicated_acme/objects/<model("cpabooks_dedicated_acme.cpabooks_dedicated_acme"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('cpabooks_dedicated_acme.object', {
#             'object': obj
#         })
