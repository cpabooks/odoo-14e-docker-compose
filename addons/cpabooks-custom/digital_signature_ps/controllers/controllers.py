# -*- coding: utf-8 -*-
# from odoo import http


# class DigitalSignaturePs(http.Controller):
#     @http.route('/digital_signature_ps/digital_signature_ps/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/digital_signature_ps/digital_signature_ps/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('digital_signature_ps.listing', {
#             'root': '/digital_signature_ps/digital_signature_ps',
#             'objects': http.request.env['digital_signature_ps.digital_signature_ps'].search([]),
#         })

#     @http.route('/digital_signature_ps/digital_signature_ps/objects/<model("digital_signature_ps.digital_signature_ps"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('digital_signature_ps.object', {
#             'object': obj
#         })
