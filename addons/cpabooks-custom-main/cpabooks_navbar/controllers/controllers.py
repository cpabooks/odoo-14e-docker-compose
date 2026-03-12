# -*- coding: utf-8 -*-
# from odoo import http


# class CpabooksNavbar(http.Controller):
#     @http.route('/cpabooks_navbar/cpabooks_navbar/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/cpabooks_navbar/cpabooks_navbar/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('cpabooks_navbar.listing', {
#             'root': '/cpabooks_navbar/cpabooks_navbar',
#             'objects': http.request.env['cpabooks_navbar.cpabooks_navbar'].search([]),
#         })

#     @http.route('/cpabooks_navbar/cpabooks_navbar/objects/<model("cpabooks_navbar.cpabooks_navbar"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('cpabooks_navbar.object', {
#             'object': obj
#         })
