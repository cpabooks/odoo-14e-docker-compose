# -*- coding: utf-8 -*-
# from odoo import http


# class CpabooksSubscriptionExtend(http.Controller):
#     @http.route('/cpabooks_subscription_extend/cpabooks_subscription_extend/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/cpabooks_subscription_extend/cpabooks_subscription_extend/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('cpabooks_subscription_extend.listing', {
#             'root': '/cpabooks_subscription_extend/cpabooks_subscription_extend',
#             'objects': http.request.env['cpabooks_subscription_extend.cpabooks_subscription_extend'].search([]),
#         })

#     @http.route('/cpabooks_subscription_extend/cpabooks_subscription_extend/objects/<model("cpabooks_subscription_extend.cpabooks_subscription_extend"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('cpabooks_subscription_extend.object', {
#             'object': obj
#         })
