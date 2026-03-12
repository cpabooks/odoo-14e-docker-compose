# -*- coding: utf-8 -*-
# from odoo import http


# class CpabookAccountingAutomation(http.Controller):
#     @http.route('/cpabook_accounting_automation/cpabook_accounting_automation/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/cpabook_accounting_automation/cpabook_accounting_automation/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('cpabook_accounting_automation.listing', {
#             'root': '/cpabook_accounting_automation/cpabook_accounting_automation',
#             'objects': http.request.env['cpabook_accounting_automation.cpabook_accounting_automation'].search([]),
#         })

#     @http.route('/cpabook_accounting_automation/cpabook_accounting_automation/objects/<model("cpabook_accounting_automation.cpabook_accounting_automation"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('cpabook_accounting_automation.object', {
#             'object': obj
#         })
