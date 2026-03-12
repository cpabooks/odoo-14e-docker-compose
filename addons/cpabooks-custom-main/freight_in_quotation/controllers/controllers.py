# -*- coding: utf-8 -*-
# from odoo import http


# class Cpataskext(http.Controller):
#     @http.route('/cpataskext/cpataskext/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/cpataskext/cpataskext/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('cpataskext.listing', {
#             'root': '/cpataskext/cpataskext',
#             'objects': http.request.env['cpataskext.cpataskext'].search([]),
#         })

#     @http.route('/cpataskext/cpataskext/objects/<model("cpataskext.cpataskext"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('cpataskext.object', {
#             'object': obj
#         })
