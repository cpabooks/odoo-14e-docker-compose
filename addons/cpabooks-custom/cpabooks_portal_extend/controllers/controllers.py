# -*- coding: utf-8 -*-
# from odoo import http


# class CpabooksPortalExtend(http.Controller):
#     @http.route('/cpabooks_portal_extend/cpabooks_portal_extend/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/cpabooks_portal_extend/cpabooks_portal_extend/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('cpabooks_portal_extend.listing', {
#             'root': '/cpabooks_portal_extend/cpabooks_portal_extend',
#             'objects': http.request.env['cpabooks_portal_extend.cpabooks_portal_extend'].search([]),
#         })

#     @http.route('/cpabooks_portal_extend/cpabooks_portal_extend/objects/<model("cpabooks_portal_extend.cpabooks_portal_extend"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('cpabooks_portal_extend.object', {
#             'object': obj
#         })
