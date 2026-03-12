# -*- coding: utf-8 -*-
# from odoo import http


# class DeliveryNoteOnDeliverySlip(http.Controller):
#     @http.route('/delivery_note_on_delivery_slip/delivery_note_on_delivery_slip/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/delivery_note_on_delivery_slip/delivery_note_on_delivery_slip/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('delivery_note_on_delivery_slip.listing', {
#             'root': '/delivery_note_on_delivery_slip/delivery_note_on_delivery_slip',
#             'objects': http.request.env['delivery_note_on_delivery_slip.delivery_note_on_delivery_slip'].search([]),
#         })

#     @http.route('/delivery_note_on_delivery_slip/delivery_note_on_delivery_slip/objects/<model("delivery_note_on_delivery_slip.delivery_note_on_delivery_slip"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('delivery_note_on_delivery_slip.object', {
#             'object': obj
#         })
