# -*- coding: utf-8 -*-
# from odoo import http


# class CpabooksDedicatedAlhilal(http.Controller):
#     @http.route('/cpabooks_dedicated_alhilal/cpabooks_dedicated_alhilal/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/cpabooks_dedicated_alhilal/cpabooks_dedicated_alhilal/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('cpabooks_dedicated_alhilal.listing', {
#             'root': '/cpabooks_dedicated_alhilal/cpabooks_dedicated_alhilal',
#             'objects': http.request.env['cpabooks_dedicated_alhilal.cpabooks_dedicated_alhilal'].search([]),
#         })

#     @http.route('/cpabooks_dedicated_alhilal/cpabooks_dedicated_alhilal/objects/<model("cpabooks_dedicated_alhilal.cpabooks_dedicated_alhilal"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('cpabooks_dedicated_alhilal.object', {
#             'object': obj
#         })
