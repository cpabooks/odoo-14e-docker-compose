# -*- coding: utf-8 -*-
# from odoo import http


# class CpabooksPartnerCodePt(http.Controller):
#     @http.route('/cpabooks_partner_code_pt/cpabooks_partner_code_pt/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/cpabooks_partner_code_pt/cpabooks_partner_code_pt/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('cpabooks_partner_code_pt.listing', {
#             'root': '/cpabooks_partner_code_pt/cpabooks_partner_code_pt',
#             'objects': http.request.env['cpabooks_partner_code_pt.cpabooks_partner_code_pt'].search([]),
#         })

#     @http.route('/cpabooks_partner_code_pt/cpabooks_partner_code_pt/objects/<model("cpabooks_partner_code_pt.cpabooks_partner_code_pt"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('cpabooks_partner_code_pt.object', {
#             'object': obj
#         })
