# -*- coding: utf-8 -*-
# from odoo import http


# class CpabooksAdminPower(http.Controller):
#     @http.route('/cpabooks_admin_power/cpabooks_admin_power/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/cpabooks_admin_power/cpabooks_admin_power/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('cpabooks_admin_power.listing', {
#             'root': '/cpabooks_admin_power/cpabooks_admin_power',
#             'objects': http.request.env['cpabooks_admin_power.cpabooks_admin_power'].search([]),
#         })

#     @http.route('/cpabooks_admin_power/cpabooks_admin_power/objects/<model("cpabooks_admin_power.cpabooks_admin_power"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('cpabooks_admin_power.object', {
#             'object': obj
#         })
