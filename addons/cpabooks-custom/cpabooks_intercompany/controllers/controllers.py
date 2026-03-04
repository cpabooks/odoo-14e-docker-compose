# -*- coding: utf-8 -*-
# from odoo import http


# class CpabooksIntercompany(http.Controller):
#     @http.route('/cpabooks_intercompany/cpabooks_intercompany/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/cpabooks_intercompany/cpabooks_intercompany/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('cpabooks_intercompany.listing', {
#             'root': '/cpabooks_intercompany/cpabooks_intercompany',
#             'objects': http.request.env['cpabooks_intercompany.cpabooks_intercompany'].search([]),
#         })

#     @http.route('/cpabooks_intercompany/cpabooks_intercompany/objects/<model("cpabooks_intercompany.cpabooks_intercompany"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('cpabooks_intercompany.object', {
#             'object': obj
#         })
