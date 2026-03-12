# -*- coding: utf-8 -*-
# from odoo import http


# class CpabooksDedicatedIdesign(http.Controller):
#     @http.route('/cpabooks_dedicated_idesign/cpabooks_dedicated_idesign/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/cpabooks_dedicated_idesign/cpabooks_dedicated_idesign/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('cpabooks_dedicated_idesign.listing', {
#             'root': '/cpabooks_dedicated_idesign/cpabooks_dedicated_idesign',
#             'objects': http.request.env['cpabooks_dedicated_idesign.cpabooks_dedicated_idesign'].search([]),
#         })

#     @http.route('/cpabooks_dedicated_idesign/cpabooks_dedicated_idesign/objects/<model("cpabooks_dedicated_idesign.cpabooks_dedicated_idesign"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('cpabooks_dedicated_idesign.object', {
#             'object': obj
#         })
