# -*- coding: utf-8 -*-
# from odoo import http


# class CpabooksDailyReports(http.Controller):
#     @http.route('/cpabooks_daily_reports/cpabooks_daily_reports/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/cpabooks_daily_reports/cpabooks_daily_reports/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('cpabooks_daily_reports.listing', {
#             'root': '/cpabooks_daily_reports/cpabooks_daily_reports',
#             'objects': http.request.env['cpabooks_daily_reports.cpabooks_daily_reports'].search([]),
#         })

#     @http.route('/cpabooks_daily_reports/cpabooks_daily_reports/objects/<model("cpabooks_daily_reports.cpabooks_daily_reports"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('cpabooks_daily_reports.object', {
#             'object': obj
#         })
