# -*- coding: utf-8 -*-
# from odoo import http


# class CpabooksQuotationReplicateToRfq(http.Controller):
#     @http.route('/cpabooks_quotation_replicate_to_rfq/cpabooks_quotation_replicate_to_rfq/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/cpabooks_quotation_replicate_to_rfq/cpabooks_quotation_replicate_to_rfq/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('cpabooks_quotation_replicate_to_rfq.listing', {
#             'root': '/cpabooks_quotation_replicate_to_rfq/cpabooks_quotation_replicate_to_rfq',
#             'objects': http.request.env['cpabooks_quotation_replicate_to_rfq.cpabooks_quotation_replicate_to_rfq'].search([]),
#         })

#     @http.route('/cpabooks_quotation_replicate_to_rfq/cpabooks_quotation_replicate_to_rfq/objects/<model("cpabooks_quotation_replicate_to_rfq.cpabooks_quotation_replicate_to_rfq"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('cpabooks_quotation_replicate_to_rfq.object', {
#             'object': obj
#         })
