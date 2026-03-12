# -*- coding: utf-8 -*-
# from odoo import http


# class CpabooksImage(http.Controller):
#     @http.route('/cpabooks_image/cpabooks_image/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/cpabooks_image/cpabooks_image/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('cpabooks_image.listing', {
#             'root': '/cpabooks_image/cpabooks_image',
#             'objects': http.request.env['cpabooks_image.cpabooks_image'].search([]),
#         })

#     @http.route('/cpabooks_image/cpabooks_image/objects/<model("cpabooks_image.cpabooks_image"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('cpabooks_image.object', {
#             'object': obj
#         })
