# -*- coding: utf-8 -*-
# from odoo import http


# class CpabooksSignature(http.Controller):
#     @http.route('/cpabooks_signature/cpabooks_signature/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/cpabooks_signature/cpabooks_signature/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('cpabooks_signature.listing', {
#             'root': '/cpabooks_signature/cpabooks_signature',
#             'objects': http.request.env['cpabooks_signature.cpabooks_signature'].search([]),
#         })

#     @http.route('/cpabooks_signature/cpabooks_signature/objects/<model("cpabooks_signature.cpabooks_signature"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('cpabooks_signature.object', {
#             'object': obj
#         })
