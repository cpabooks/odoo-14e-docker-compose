# -*- coding: utf-8 -*-
# from odoo import http


# class CpabooksHelpdeskExtend(http.Controller):
#     @http.route('/cpabooks_helpdesk_extend/cpabooks_helpdesk_extend/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/cpabooks_helpdesk_extend/cpabooks_helpdesk_extend/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('cpabooks_helpdesk_extend.listing', {
#             'root': '/cpabooks_helpdesk_extend/cpabooks_helpdesk_extend',
#             'objects': http.request.env['cpabooks_helpdesk_extend.cpabooks_helpdesk_extend'].search([]),
#         })

#     @http.route('/cpabooks_helpdesk_extend/cpabooks_helpdesk_extend/objects/<model("cpabooks_helpdesk_extend.cpabooks_helpdesk_extend"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('cpabooks_helpdesk_extend.object', {
#             'object': obj
#         })
