# -*- coding: utf-8 -*-
# from odoo import http


# class CpabooksManufacturingExtend(http.Controller):
#     @http.route('/cpabooks_manufacturing_extend/cpabooks_manufacturing_extend/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/cpabooks_manufacturing_extend/cpabooks_manufacturing_extend/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('cpabooks_manufacturing_extend.listing', {
#             'root': '/cpabooks_manufacturing_extend/cpabooks_manufacturing_extend',
#             'objects': http.request.env['cpabooks_manufacturing_extend.cpabooks_manufacturing_extend'].search([]),
#         })

#     @http.route('/cpabooks_manufacturing_extend/cpabooks_manufacturing_extend/objects/<model("cpabooks_manufacturing_extend.cpabooks_manufacturing_extend"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('cpabooks_manufacturing_extend.object', {
#             'object': obj
#         })
