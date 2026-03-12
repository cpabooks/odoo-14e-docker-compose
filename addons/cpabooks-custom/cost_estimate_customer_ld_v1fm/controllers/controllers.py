# -*- coding: utf-8 -*-
# from odoo import http


# class CostEstimateCustomerLdV1fm(http.Controller):
#     @http.route('/cost_estimate_customer_ld_v1fm/cost_estimate_customer_ld_v1fm/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/cost_estimate_customer_ld_v1fm/cost_estimate_customer_ld_v1fm/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('cost_estimate_customer_ld_v1fm.listing', {
#             'root': '/cost_estimate_customer_ld_v1fm/cost_estimate_customer_ld_v1fm',
#             'objects': http.request.env['cost_estimate_customer_ld_v1fm.cost_estimate_customer_ld_v1fm'].search([]),
#         })

#     @http.route('/cost_estimate_customer_ld_v1fm/cost_estimate_customer_ld_v1fm/objects/<model("cost_estimate_customer_ld_v1fm.cost_estimate_customer_ld_v1fm"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('cost_estimate_customer_ld_v1fm.object', {
#             'object': obj
#         })
