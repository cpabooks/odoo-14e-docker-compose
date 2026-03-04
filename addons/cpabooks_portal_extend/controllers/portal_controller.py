from odoo.addons.portal.controllers.portal import CustomerPortal, pager
from odoo.http import request
from odoo import http
from werkzeug.utils import redirect
import base64
import mimetypes


class DocumentsPortals(CustomerPortal):

    def _prepare_home_portal_values(self, counters):
        rtn = super(DocumentsPortals, self)._prepare_home_portal_values(counters)
        rtn['documents_count'] = request.env['documents.document'].search_count([('owner_id','=',request.env.user.id)])

        return rtn

    @http.route(['/my/documents','/my/documents/page/<int:page>'], type='http', website=True)
    def documents_list(self, page=1, **kwargs):
        total_docs = request.env['documents.document'].search_count([('owner_id','=',request.env.user.id)])
        page_details = pager(url='/my/documents',total=total_docs,page=page,step=15)

        documents = request.env['documents.document'].search([('owner_id','=',request.env.user.id)], limit=5, offset=page_details['offset'])
        context = {
            'documents': documents,
            'page_name': 'document_list_view',
            'pager': page_details,
        }

        return request.render('cpabooks_portal_extend.documents_list_view_template', context)

    @http.route(['/my/documents/<model("documents.document"):doc>/download'], type='http', website=True)
    def download_document(self, doc, **kwargs):
        if not doc.exists():
            return redirect('/404')

        data = base64.b64decode(doc.datas)
        filename = doc.name

        headers = [('Content-Type', 'application/octet-stream'),
                   ('Content-Disposition', f'attachment; filename="{filename}"')]

        return request.make_response(data, headers=headers)

    @http.route(['/my/documents/<model("documents.document"):doc>/preview'], type='http', website=True)
    def preview_document(self, doc, **kwargs):
        if not doc.exists():
            return request.not_found()
        data = base64.b64decode(doc.datas)
        filename = doc.name

        content_type, _ = mimetypes.guess_type(filename)

        headers = [('Content-Disposition', f'inline; filename="{filename}"')]
        if content_type:
            headers.append(('Content-Type', content_type))
        return request.make_response(data, headers=headers)