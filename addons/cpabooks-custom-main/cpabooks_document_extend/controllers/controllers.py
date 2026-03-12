# -*- coding: utf-8 -*-
# from odoo import http


# class CpabooksDocumentExtend(http.Controller):
#     @http.route('/cpabooks_document_extend/cpabooks_document_extend/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/cpabooks_document_extend/cpabooks_document_extend/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('cpabooks_document_extend.listing', {
#             'root': '/cpabooks_document_extend/cpabooks_document_extend',
#             'objects': http.request.env['cpabooks_document_extend.cpabooks_document_extend'].search([]),
#         })

#     @http.route('/cpabooks_document_extend/cpabooks_document_extend/objects/<model("cpabooks_document_extend.cpabooks_document_extend"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('cpabooks_document_extend.object', {
#             'object': obj
#         })
