# -*- coding: utf-8 -*-
# from odoo import http


# class CpabooksImportPurchase(http.Controller):
#     @http.route('/cpabooks_import_purchase/cpabooks_import_purchase/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/cpabooks_import_purchase/cpabooks_import_purchase/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('cpabooks_import_purchase.listing', {
#             'root': '/cpabooks_import_purchase/cpabooks_import_purchase',
#             'objects': http.request.env['cpabooks_import_purchase.cpabooks_import_purchase'].search([]),
#         })

#     @http.route('/cpabooks_import_purchase/cpabooks_import_purchase/objects/<model("cpabooks_import_purchase.cpabooks_import_purchase"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('cpabooks_import_purchase.object', {
#             'object': obj
#         })
