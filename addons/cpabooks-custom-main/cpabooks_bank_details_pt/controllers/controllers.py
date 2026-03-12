# -*- coding: utf-8 -*-
# from odoo import http


# class CpabooksBankDetailsPt(http.Controller):
#     @http.route('/cpabooks_bank_details_pt/cpabooks_bank_details_pt/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/cpabooks_bank_details_pt/cpabooks_bank_details_pt/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('cpabooks_bank_details_pt.listing', {
#             'root': '/cpabooks_bank_details_pt/cpabooks_bank_details_pt',
#             'objects': http.request.env['cpabooks_bank_details_pt.cpabooks_bank_details_pt'].search([]),
#         })

#     @http.route('/cpabooks_bank_details_pt/cpabooks_bank_details_pt/objects/<model("cpabooks_bank_details_pt.cpabooks_bank_details_pt"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('cpabooks_bank_details_pt.object', {
#             'object': obj
#         })
