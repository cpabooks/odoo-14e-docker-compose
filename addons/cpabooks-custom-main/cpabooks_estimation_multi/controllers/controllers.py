# -*- coding: utf-8 -*-
# from odoo import http


# class CpabooksEstimationMulti(http.Controller):
#     @http.route('/cpabooks_estimation_multi/cpabooks_estimation_multi/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/cpabooks_estimation_multi/cpabooks_estimation_multi/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('cpabooks_estimation_multi.listing', {
#             'root': '/cpabooks_estimation_multi/cpabooks_estimation_multi',
#             'objects': http.request.env['cpabooks_estimation_multi.cpabooks_estimation_multi'].search([]),
#         })

#     @http.route('/cpabooks_estimation_multi/cpabooks_estimation_multi/objects/<model("cpabooks_estimation_multi.cpabooks_estimation_multi"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('cpabooks_estimation_multi.object', {
#             'object': obj
#         })
