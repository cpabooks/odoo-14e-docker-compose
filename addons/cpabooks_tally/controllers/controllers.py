# -*- coding: utf-8 -*-
# from odoo import http


# class CpabooksTally(http.Controller):
#     @http.route('/cpabooks_tally/cpabooks_tally/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/cpabooks_tally/cpabooks_tally/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('cpabooks_tally.listing', {
#             'root': '/cpabooks_tally/cpabooks_tally',
#             'objects': http.request.env['cpabooks_tally.cpabooks_tally'].search([]),
#         })

#     @http.route('/cpabooks_tally/cpabooks_tally/objects/<model("cpabooks_tally.cpabooks_tally"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('cpabooks_tally.object', {
#             'object': obj
#         })
