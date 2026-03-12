# -*- coding: utf-8 -*-
# from odoo import http


# class CpabooksItemCodeAutoIncreament(http.Controller):
#     @http.route('/cpabooks_item_code_auto_increament/cpabooks_item_code_auto_increament/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/cpabooks_item_code_auto_increament/cpabooks_item_code_auto_increament/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('cpabooks_item_code_auto_increament.listing', {
#             'root': '/cpabooks_item_code_auto_increament/cpabooks_item_code_auto_increament',
#             'objects': http.request.env['cpabooks_item_code_auto_increament.cpabooks_item_code_auto_increament'].search([]),
#         })

#     @http.route('/cpabooks_item_code_auto_increament/cpabooks_item_code_auto_increament/objects/<model("cpabooks_item_code_auto_increament.cpabooks_item_code_auto_increament"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('cpabooks_item_code_auto_increament.object', {
#             'object': obj
#         })
