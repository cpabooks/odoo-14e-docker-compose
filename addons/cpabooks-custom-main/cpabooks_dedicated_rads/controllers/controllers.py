# -*- coding: utf-8 -*-
# from odoo import http


# class CpabooksDedicatedRads(http.Controller):
#     @http.route('/cpabooks_dedicated_rads/cpabooks_dedicated_rads/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/cpabooks_dedicated_rads/cpabooks_dedicated_rads/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('cpabooks_dedicated_rads.listing', {
#             'root': '/cpabooks_dedicated_rads/cpabooks_dedicated_rads',
#             'objects': http.request.env['cpabooks_dedicated_rads.cpabooks_dedicated_rads'].search([]),
#         })

#     @http.route('/cpabooks_dedicated_rads/cpabooks_dedicated_rads/objects/<model("cpabooks_dedicated_rads.cpabooks_dedicated_rads"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('cpabooks_dedicated_rads.object', {
#             'object': obj
#         })
