# -*- coding: utf-8 -*-
# from odoo import http


# class CpabooksDedicatedFoodEnergy(http.Controller):
#     @http.route('/cpabooks_dedicated_food_energy/cpabooks_dedicated_food_energy/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/cpabooks_dedicated_food_energy/cpabooks_dedicated_food_energy/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('cpabooks_dedicated_food_energy.listing', {
#             'root': '/cpabooks_dedicated_food_energy/cpabooks_dedicated_food_energy',
#             'objects': http.request.env['cpabooks_dedicated_food_energy.cpabooks_dedicated_food_energy'].search([]),
#         })

#     @http.route('/cpabooks_dedicated_food_energy/cpabooks_dedicated_food_energy/objects/<model("cpabooks_dedicated_food_energy.cpabooks_dedicated_food_energy"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('cpabooks_dedicated_food_energy.object', {
#             'object': obj
#         })
