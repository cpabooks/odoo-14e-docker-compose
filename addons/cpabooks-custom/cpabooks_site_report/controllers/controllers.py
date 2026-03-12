# -*- coding: utf-8 -*-
# from odoo import http


# class CpabooksSiteReport(http.Controller):
#     @http.route('/cpabooks_site_report/cpabooks_site_report/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/cpabooks_site_report/cpabooks_site_report/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('cpabooks_site_report.listing', {
#             'root': '/cpabooks_site_report/cpabooks_site_report',
#             'objects': http.request.env['cpabooks_site_report.cpabooks_site_report'].search([]),
#         })

#     @http.route('/cpabooks_site_report/cpabooks_site_report/objects/<model("cpabooks_site_report.cpabooks_site_report"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('cpabooks_site_report.object', {
#             'object': obj
#         })
