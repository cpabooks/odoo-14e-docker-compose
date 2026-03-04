# -*- coding: utf-8 -*-
# from odoo import http


# class TestModule(http.Controller):
#     @http.route('/cpabooks_digital_signature_ptv1/cpabooks_digital_signature_ptv1/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/cpabooks_digital_signature_ptv1/cpabooks_digital_signature_ptv1/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('cpabooks_digital_signature_ptv1.listing', {
#             'root': '/cpabooks_digital_signature_ptv1/cpabooks_digital_signature_ptv1',
#             'objects': http.request.env['cpabooks_digital_signature_ptv1.cpabooks_digital_signature_ptv1'].search([]),
#         })

#     @http.route('/cpabooks_digital_signature_ptv1/cpabooks_digital_signature_ptv1/objects/<model("cpabooks_digital_signature_ptv1.cpabooks_digital_signature_ptv1"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('cpabooks_digital_signature_ptv1.object', {
#             'object': obj
#         })
