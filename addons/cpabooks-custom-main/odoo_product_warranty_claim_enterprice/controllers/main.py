# -*- coding: utf-8 -*-

import base64
from odoo import http, _
from odoo.http import request
from odoo import models,registry, SUPERUSER_ID
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager, get_records_pager
from odoo.osv.expression import OR

class HelpdeskSupportEnterprice(http.Controller):

    @http.route(['/odoo_product_warranty_claim_enterprice/ticket_submitted'], type='http', auth="user", methods=['POST'], website=True)
    def ticket_enterprice_submitted(self, **post):
        cr, uid, context, pool = http.request.cr, http.request.uid, http.request.context, request.env
        if request.env.user.has_group('base.group_public'):
            Partner = request.env['res.partner'].sudo().search([('email', '=', post['email'])], limit=1)
        else:
            Partner = request.env.user.partner_id
       
        if Partner:
#             team_obj = http.request.env['support.team']
#             team_match = team_obj.sudo().search([('is_team','=', True)], limit=1)
            if post['warranty_number']:
                warranty_id = request.env['product.warranty.registration'].sudo().search([
                   ('name', 'ilike', str(post['warranty_number']))
                ])
            support = request.env['helpdesk.ticket'].sudo().create({
                                                            # 'subject': post['subject'], #odoo13
                                                            'name': post['subject'],
#                                                             'team_id' :team_match.id,
                                                            #'partner_id' :team_match.leader_id.id,
#                                                             'user_id' :team_match.leader_id.id,
#                                                             'team_leader_id': team_match.leader_id.id,
                                                            'email': post['email'],
                                                            'custom_phone': post['phone'],
                                                            'custom_category': post['category'],
                                                            'description': post['description'],
                                                            'priority': post['priority'],
                                                            'partner_id': Partner.id,
                                                            'custom_serial_number': post['serial_number'],
                                                            'custom_contract_reference': post['contract_reference'],
                                                            'custom_warranty_number': post['warranty_number'],
                                                            'custom_warranty_start_date': post['warranty_start_date'],
                                                            'custom_warranty_end_date': post['warranty_end_date'],
                                                            'custom_warranty_id': warranty_id.id or False,
                                                            'custom_is_claim' : True,
                                                             })
            values = {
                'support':support,
            }
            attachment_list = request.httprequest.files.getlist('attachment')
            for image in attachment_list:
                if post.get('attachment'):
                    attachments = {
                               'res_name': image.filename,
                               'res_model': 'helpdesk.ticket',
                               'res_id': support,
                               'datas': base64.encodestring(image.read()),
                               'type': 'binary',
                               # 'datas_fname': image.filename,
                               'name': image.filename,
                           }
                    attachment_obj = http.request.env['ir.attachment']
                    attach = attachment_obj.sudo().create(attachments)
            if len(attachment_list) > 0:
                group_msg = 'Customer has sent %s attachments to this helpdesk ticket. Name of attachments are: ' % (len(attachment_list))
                for attach in attachment_list:
                    group_msg = group_msg + '\n' + attach.filename
                group_msg = group_msg + '\n'  +  '. You can see top attachment menu to download attachments.'
                support.sudo().message_post(body=_(group_msg),message_type='comment')
                    
            return request.render('odoo_product_warranty_claim_enterprice.thanks_mail_send_custom_claim_enterprice', values)
        else:
            return request.render('odoo_product_warranty_claim_enterprice.support_ticket_invalid_custom_claim_enterprice',{})

class CustomerPortal(CustomerPortal):
    
    def _prepare_portal_layout_values(self):
        values = super(CustomerPortal, self)._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        product_warranty = request.env['product.warranty.registration']
        warranty_claim_count = product_warranty.sudo().search_count(
            [('partner_id', 'child_of', [partner.commercial_partner_id.id])]
        )
        claim_obj = request.env['helpdesk.ticket']
        domain = [
            ('custom_is_claim', '=', True)
        ]
        claim_count = claim_obj.sudo().search_count(domain)
        values.update({
            'warranty_claim_count': warranty_claim_count,
            'claim_count' : claim_count,
        })
        return values

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        partner = request.env.user.partner_id
        product_warranty = request.env['product.warranty.registration']
        warranty_claim_count = product_warranty.sudo().search_count(
            [('partner_id', 'child_of', [partner.commercial_partner_id.id])]
        )
        claim_obj = request.env['helpdesk.ticket']
        domain = [
            ('custom_is_claim', '=', True)
        ]
        claim_count = claim_obj.sudo().search_count(domain)
        values.update({
            'warranty_claim_count': warranty_claim_count,
            'claim_count' : claim_count,
        })
        return values

#     @http.route(['/create_warranty_claims'], type='http', auth="user", website=True)
#     def portal_create_warranty_claims(self, page=1, **kw):
#         print ("odoo_product_warranty_claimffffffffffffffffffffffffffffffffff")
#         warranty_ids = request.env['product.warranty.registration'].search([
#            ('partner_id', '=', request.env.user.partner_id.id)
#         ])
#         contract_ids = request.env['account.analytic.account'].search([
#            ('partner_id', '=', request.env.user.partner_id.id)
#         ])
#         
#         values = {
#             'warrantys': warranty_ids,
#             'contracts': contract_ids
#         }
#         return request.render("odoo_product_warranty_claim_enterprice.helpdesk_support_ticket_inherit_warranty_claim", values)

    @http.route(['/my/warranty_claims_enterprice', '/my/warranty_claims_enterprice/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_warranty_claims_enterprice(self, page=1, **kw):
        response = super(CustomerPortal, self)
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        warranty_obj = request.env['product.warranty.registration']
        domain = [
            ('partner_id', 'child_of', [partner.commercial_partner_id.id])
        ]
        # count for pager
        warranty_claim_count = warranty_obj.sudo().search_count(domain)
        # pager
        pager = request.website.pager(
            url="/my/warranty_claims_enterprice",
            total=warranty_claim_count,
            page=page,
            step=self._items_per_page
        )
        # content according to pager and archive selected
        warranty_claims = warranty_obj.sudo().search(domain, limit=self._items_per_page, offset=pager['offset'])
        values.update({
            'warranty_claims': warranty_claims,
            'page_name': 'warranty_claim',
            'pager': pager,
            'default_url': '/my/warranty_claims_enterprice',
        })
        return request.render("odoo_product_warranty_claim_enterprice.display_warranty_claims_enterprice", values)
        
        
    @http.route(['/my/claims_enterprice', '/my/claims_enterprice/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_claims_enterprice(self, page=1,sortby=None, search=None, search_in='content', **kw):
        values = self._prepare_portal_layout_values()
        
        domain = []

        searchbar_sortings = {
            'date': {'label': _('Newest'), 'order': 'create_date desc'},
            'name': {'label': _('Subject'), 'order': 'name'},
        }
        searchbar_inputs = {
            'content': {'input': 'content', 'label': _('Search <span class="nolabel"> (in Content)</span>')},
            'message': {'input': 'message', 'label': _('Search in Messages')},
            'customer': {'input': 'customer', 'label': _('Search in Customer')},
            'all': {'input': 'all', 'label': _('Search in All')},
        }

        # default sort by value
        if not sortby:
            sortby = 'date'
        order = searchbar_sortings[sortby]['order']
        
        # search
        if search and search_in:
            search_domain = []
            if search_in in ('content', 'all'):
                search_domain = OR([search_domain, ['|', ('name', 'ilike', search), ('description', 'ilike', search)]])
            if search_in in ('customer', 'all'):
                search_domain = OR([search_domain, [('partner_id', 'ilike', search)]])
            if search_in in ('message', 'all'):
                search_domain = OR([search_domain, [('message_ids.body', 'ilike', search)]])
            domain += search_domain
        
        domain += ([('custom_is_claim','=',True)])
            
        # pager
        claim_count = request.env['helpdesk.ticket'].search_count(domain)
        pager = portal_pager(
            url="/my/claims",
            total=claim_count,
            page=page,
            step=self._items_per_page
        )
        
        tickets = request.env['helpdesk.ticket'].search(domain, order=order, limit=self._items_per_page, offset=pager['offset'])
        
#        values.update({
#            'tickets': tickets,
#            'page_name': 'ticket',
#            'default_url': '/my/claims',
#        })
        
        values.update({
            'grouped_tickets': tickets,
            'page_name': 'ticket',
            'default_url': '/my/claims',
            'pager': pager,
            'searchbar_sortings': searchbar_sortings,
            'searchbar_inputs': searchbar_inputs,
            'sortby': sortby,
            'search_in': search_in,
            'search': search,
        })
        return request.render("helpdesk.portal_helpdesk_ticket", values)
        
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
