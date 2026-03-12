# -*- coding: utf-8 -*-
# from odoo import http


# class CpabooksItemCodesPt(http.Controller):
#     @http.route('/cpabooks_item_codes_pt/cpabooks_item_codes_pt/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/cpabooks_item_codes_pt/cpabooks_item_codes_pt/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('cpabooks_item_codes_pt.listing', {
#             'root': '/cpabooks_item_codes_pt/cpabooks_item_codes_pt',
#             'objects': http.request.env['cpabooks_item_codes_pt.cpabooks_item_codes_pt'].search([]),
#         })

#     @http.route('/cpabooks_item_codes_pt/cpabooks_item_codes_pt/objects/<model("cpabooks_item_codes_pt.cpabooks_item_codes_pt"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('cpabooks_item_codes_pt.object', {
#             'object': obj
#         })
