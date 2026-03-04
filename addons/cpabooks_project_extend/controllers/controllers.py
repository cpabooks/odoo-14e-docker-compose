# -*- coding: utf-8 -*-
# from odoo import http


# class CpabooksProjectExtend(http.Controller):
#     @http.route('/cpabooks_project_extend/cpabooks_project_extend/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/cpabooks_project_extend/cpabooks_project_extend/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('cpabooks_project_extend.listing', {
#             'root': '/cpabooks_project_extend/cpabooks_project_extend',
#             'objects': http.request.env['cpabooks_project_extend.cpabooks_project_extend'].search([]),
#         })

#     @http.route('/cpabooks_project_extend/cpabooks_project_extend/objects/<model("cpabooks_project_extend.cpabooks_project_extend"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('cpabooks_project_extend.object', {
#             'object': obj
#         })
