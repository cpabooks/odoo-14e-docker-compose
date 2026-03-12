# -*- coding: utf-8 -*-
# from odoo import http


# class CpabooksDeliveryStatusOnSalesOrder(http.Controller):
#     @http.route('/cpabooks_delivery_status_on_sales_order/cpabooks_delivery_status_on_sales_order/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/cpabooks_delivery_status_on_sales_order/cpabooks_delivery_status_on_sales_order/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('cpabooks_delivery_status_on_sales_order.listing', {
#             'root': '/cpabooks_delivery_status_on_sales_order/cpabooks_delivery_status_on_sales_order',
#             'objects': http.request.env['cpabooks_delivery_status_on_sales_order.cpabooks_delivery_status_on_sales_order'].search([]),
#         })

#     @http.route('/cpabooks_delivery_status_on_sales_order/cpabooks_delivery_status_on_sales_order/objects/<model("cpabooks_delivery_status_on_sales_order.cpabooks_delivery_status_on_sales_order"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('cpabooks_delivery_status_on_sales_order.object', {
#             'object': obj
#         })
