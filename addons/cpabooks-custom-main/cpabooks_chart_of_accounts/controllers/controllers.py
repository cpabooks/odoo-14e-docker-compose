# -*- coding: utf-8 -*-
# from odoo import http


# class CpabooksChartOfAccounts(http.Controller):
#     @http.route('/cpabooks_chart_of_accounts/cpabooks_chart_of_accounts/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/cpabooks_chart_of_accounts/cpabooks_chart_of_accounts/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('cpabooks_chart_of_accounts.listing', {
#             'root': '/cpabooks_chart_of_accounts/cpabooks_chart_of_accounts',
#             'objects': http.request.env['cpabooks_chart_of_accounts.cpabooks_chart_of_accounts'].search([]),
#         })

#     @http.route('/cpabooks_chart_of_accounts/cpabooks_chart_of_accounts/objects/<model("cpabooks_chart_of_accounts.cpabooks_chart_of_accounts"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('cpabooks_chart_of_accounts.object', {
#             'object': obj
#         })
