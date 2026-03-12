# -*- coding: utf-8 -*-
# from odoo import http


# class CpbaooksDedicated4star(http.Controller):
#     @http.route('/cpbaooks_dedicated_4star/cpbaooks_dedicated_4star/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/cpbaooks_dedicated_4star/cpbaooks_dedicated_4star/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('cpbaooks_dedicated_4star.listing', {
#             'root': '/cpbaooks_dedicated_4star/cpbaooks_dedicated_4star',
#             'objects': http.request.env['cpbaooks_dedicated_4star.cpbaooks_dedicated_4star'].search([]),
#         })

#     @http.route('/cpbaooks_dedicated_4star/cpbaooks_dedicated_4star/objects/<model("cpbaooks_dedicated_4star.cpbaooks_dedicated_4star"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('cpbaooks_dedicated_4star.object', {
#             'object': obj
#         })
