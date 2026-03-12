# -*- coding: utf-8 -*-
# from odoo import http


# class CpabooksHeaderFooterLogoPt(http.Controller):
#     @http.route('/cpabooks_header_footer_logo_pt/cpabooks_header_footer_logo_pt/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/cpabooks_header_footer_logo_pt/cpabooks_header_footer_logo_pt/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('cpabooks_header_footer_logo_pt.listing', {
#             'root': '/cpabooks_header_footer_logo_pt/cpabooks_header_footer_logo_pt',
#             'objects': http.request.env['cpabooks_header_footer_logo_pt.cpabooks_header_footer_logo_pt'].search([]),
#         })

#     @http.route('/cpabooks_header_footer_logo_pt/cpabooks_header_footer_logo_pt/objects/<model("cpabooks_header_footer_logo_pt.cpabooks_header_footer_logo_pt"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('cpabooks_header_footer_logo_pt.object', {
#             'object': obj
#         })
