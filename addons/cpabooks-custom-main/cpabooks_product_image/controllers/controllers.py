# -*- coding: utf-8 -*-
# from odoo import http


# class BtUploadImageInQuotationLine(http.Controller):
#     @http.route('/bt_upload_image_in_quotation_line/bt_upload_image_in_quotation_line', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/bt_upload_image_in_quotation_line/bt_upload_image_in_quotation_line/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('bt_upload_image_in_quotation_line.listing', {
#             'root': '/bt_upload_image_in_quotation_line/bt_upload_image_in_quotation_line',
#             'objects': http.request.env['bt_upload_image_in_quotation_line.bt_upload_image_in_quotation_line'].search([]),
#         })

#     @http.route('/bt_upload_image_in_quotation_line/bt_upload_image_in_quotation_line/objects/<model("bt_upload_image_in_quotation_line.bt_upload_image_in_quotation_line"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('bt_upload_image_in_quotation_line.object', {
#             'object': obj
#         })
