# -*- coding: utf-8 -*-
# from odoo import http


# class CpabooksHideApp(http.Controller):
#     @http.route('/cpabooks_hide_app/cpabooks_hide_app/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/cpabooks_hide_app/cpabooks_hide_app/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('cpabooks_hide_app.listing', {
#             'root': '/cpabooks_hide_app/cpabooks_hide_app',
#             'objects': http.request.env['cpabooks_hide_app.cpabooks_hide_app'].search([]),
#         })

#     @http.route('/cpabooks_hide_app/cpabooks_hide_app/objects/<model("cpabooks_hide_app.cpabooks_hide_app"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('cpabooks_hide_app.object', {
#             'object': obj
#         })
