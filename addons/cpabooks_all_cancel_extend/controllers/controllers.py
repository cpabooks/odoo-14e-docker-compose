# -*- coding: utf-8 -*-
# from odoo import http


# class CpabooksAllCancelExtend(http.Controller):
#     @http.route('/cpabooks_all_cancel_extend/cpabooks_all_cancel_extend/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/cpabooks_all_cancel_extend/cpabooks_all_cancel_extend/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('cpabooks_all_cancel_extend.listing', {
#             'root': '/cpabooks_all_cancel_extend/cpabooks_all_cancel_extend',
#             'objects': http.request.env['cpabooks_all_cancel_extend.cpabooks_all_cancel_extend'].search([]),
#         })

#     @http.route('/cpabooks_all_cancel_extend/cpabooks_all_cancel_extend/objects/<model("cpabooks_all_cancel_extend.cpabooks_all_cancel_extend"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('cpabooks_all_cancel_extend.object', {
#             'object': obj
#         })
