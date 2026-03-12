# -*- coding: utf-8 -*-
# from odoo import http


# class CpabooksJobOrder(http.Controller):
#     @http.route('/cpabooks_job_order/cpabooks_job_order/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/cpabooks_job_order/cpabooks_job_order/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('cpabooks_job_order.listing', {
#             'root': '/cpabooks_job_order/cpabooks_job_order',
#             'objects': http.request.env['cpabooks_job_order.cpabooks_job_order'].search([]),
#         })

#     @http.route('/cpabooks_job_order/cpabooks_job_order/objects/<model("cpabooks_job_order.cpabooks_job_order"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('cpabooks_job_order.object', {
#             'object': obj
#         })
