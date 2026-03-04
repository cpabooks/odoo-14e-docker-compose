# -*- coding: utf-8 -*-
# from odoo import http


# class CpabooksFieldServieceExtend(http.Controller):
#     @http.route('/cpabooks_field_serviece_extend/cpabooks_field_serviece_extend/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/cpabooks_field_serviece_extend/cpabooks_field_serviece_extend/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('cpabooks_field_serviece_extend.listing', {
#             'root': '/cpabooks_field_serviece_extend/cpabooks_field_serviece_extend',
#             'objects': http.request.env['cpabooks_field_serviece_extend.cpabooks_field_serviece_extend'].search([]),
#         })

#     @http.route('/cpabooks_field_serviece_extend/cpabooks_field_serviece_extend/objects/<model("cpabooks_field_serviece_extend.cpabooks_field_serviece_extend"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('cpabooks_field_serviece_extend.object', {
#             'object': obj
#         })
