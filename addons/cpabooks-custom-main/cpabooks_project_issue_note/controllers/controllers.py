# -*- coding: utf-8 -*-
# from odoo import http


# class CpabooksProjectIssueNote(http.Controller):
#     @http.route('/cpabooks_project_issue_note/cpabooks_project_issue_note/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/cpabooks_project_issue_note/cpabooks_project_issue_note/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('cpabooks_project_issue_note.listing', {
#             'root': '/cpabooks_project_issue_note/cpabooks_project_issue_note',
#             'objects': http.request.env['cpabooks_project_issue_note.cpabooks_project_issue_note'].search([]),
#         })

#     @http.route('/cpabooks_project_issue_note/cpabooks_project_issue_note/objects/<model("cpabooks_project_issue_note.cpabooks_project_issue_note"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('cpabooks_project_issue_note.object', {
#             'object': obj
#         })
