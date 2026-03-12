# -*- coding: utf-8 -*-
# from odoo import http


# class CpabooksCurrencies(http.Controller):
#     @http.route('/cpabooks_currencies/cpabooks_currencies/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/cpabooks_currencies/cpabooks_currencies/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('cpabooks_currencies.listing', {
#             'root': '/cpabooks_currencies/cpabooks_currencies',
#             'objects': http.request.env['cpabooks_currencies.cpabooks_currencies'].search([]),
#         })

#     @http.route('/cpabooks_currencies/cpabooks_currencies/objects/<model("cpabooks_currencies.cpabooks_currencies"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('cpabooks_currencies.object', {
#             'object': obj
#         })
