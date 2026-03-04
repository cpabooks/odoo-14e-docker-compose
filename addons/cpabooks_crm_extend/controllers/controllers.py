# -*- coding: utf-8 -*-
# from odoo import http


# class CpabooksCrmExtend(http.Controller):
#     @http.route('/cpabooks_crm_extend/cpabooks_crm_extend/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/cpabooks_crm_extend/cpabooks_crm_extend/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('cpabooks_crm_extend.listing', {
#             'root': '/cpabooks_crm_extend/cpabooks_crm_extend',
#             'objects': http.request.env['cpabooks_crm_extend.cpabooks_crm_extend'].search([]),
#         })

#     @http.route('/cpabooks_crm_extend/cpabooks_crm_extend/objects/<model("cpabooks_crm_extend.cpabooks_crm_extend"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('cpabooks_crm_extend.object', {
#             'object': obj
#         })
