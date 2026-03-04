# -*- coding: utf-8 -*-
# from odoo import http


# class CpabooksDedicatedAme(http.Controller):
#     @http.route('/cpabooks_dedicated_ame/cpabooks_dedicated_ame/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/cpabooks_dedicated_ame/cpabooks_dedicated_ame/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('cpabooks_dedicated_ame.listing', {
#             'root': '/cpabooks_dedicated_ame/cpabooks_dedicated_ame',
#             'objects': http.request.env['cpabooks_dedicated_ame.cpabooks_dedicated_ame'].search([]),
#         })

#     @http.route('/cpabooks_dedicated_ame/cpabooks_dedicated_ame/objects/<model("cpabooks_dedicated_ame.cpabooks_dedicated_ame"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('cpabooks_dedicated_ame.object', {
#             'object': obj
#         })
