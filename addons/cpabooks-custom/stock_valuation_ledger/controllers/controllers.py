# -*- coding: utf-8 -*-
# from odoo import http


# class StockValuationLedger(http.Controller):
#     @http.route('/stock_valuation_ledger/stock_valuation_ledger/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/stock_valuation_ledger/stock_valuation_ledger/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('stock_valuation_ledger.listing', {
#             'root': '/stock_valuation_ledger/stock_valuation_ledger',
#             'objects': http.request.env['stock_valuation_ledger.stock_valuation_ledger'].search([]),
#         })

#     @http.route('/stock_valuation_ledger/stock_valuation_ledger/objects/<model("stock_valuation_ledger.stock_valuation_ledger"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('stock_valuation_ledger.object', {
#             'object': obj
#         })
