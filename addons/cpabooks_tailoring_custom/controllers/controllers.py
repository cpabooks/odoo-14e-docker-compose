# -*- coding: utf-8 -*-
# from odoo import http


# class CpabooksTailoringCustom(http.Controller):
#     @http.route('/cpabooks_tailoring_custom/cpabooks_tailoring_custom/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/cpabooks_tailoring_custom/cpabooks_tailoring_custom/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('cpabooks_tailoring_custom.listing', {
#             'root': '/cpabooks_tailoring_custom/cpabooks_tailoring_custom',
#             'objects': http.request.env['cpabooks_tailoring_custom.cpabooks_tailoring_custom'].search([]),
#         })

#     @http.route('/cpabooks_tailoring_custom/cpabooks_tailoring_custom/objects/<model("cpabooks_tailoring_custom.cpabooks_tailoring_custom"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('cpabooks_tailoring_custom.object', {
#             'object': obj
#         })
