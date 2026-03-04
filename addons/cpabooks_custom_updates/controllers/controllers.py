# -*- coding: utf-8 -*-
# from odoo import http


# class CpabooksMultiModulesUpdate(http.Controller):
#     @http.route('/cpabooks_custom_updates/cpabooks_custom_updates/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/cpabooks_custom_updates/cpabooks_custom_updates/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('cpabooks_custom_updates.listing', {
#             'root': '/cpabooks_custom_updates/cpabooks_custom_updates',
#             'objects': http.request.env['cpabooks_custom_updates.cpabooks_custom_updates'].search([]),
#         })

#     @http.route('/cpabooks_custom_updates/cpabooks_custom_updates/objects/<model("cpabooks_custom_updates.cpabooks_custom_updates"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('cpabooks_custom_updates.object', {
#             'object': obj
#         })
