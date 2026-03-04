from odoo import http
from odoo.http import request
from datetime import datetime
import base64


class CpaHelpDesk(http.Controller):

    @http.route('/web/gcl', type='http', website=True, auth='public')
    def hospital_signup(self, **kw):
        return request.render("cpahelpdesk.gcl", {})

    @http.route('/create/maintenance-request/', type='http', website=True, auth='public')
    def create_maintenance_request(self, **post):
        today = datetime.today()
        tenant = post.get('tenant', '')
        mobile = post.get('mobile', '')
        email = post.get('email', '')
        vals = {
            "building": post.get("building", ""),
            "flat": post.get("flat", ""),
            "maintenance_type": post.get("maintenance_type", ""),
            "work_type": post.get("work_type", ""),
            "problem": post.get("problem", ""),
            "name": post.get("problem_detail", ""),
            "property": post.get("property", ""),
            "address": post.get("address", ""),
        }

        tenant_id = request.env['maintenance.tenant'].sudo().search([
            ('email', '=', email),
        ], limit=1)
        if not tenant_id:
            tenant_id = request.env['maintenance.tenant'].sudo().create({
                'name': tenant,
                'mobile': mobile,
                'email': email,
            })
            # 'ticket_no':
        maintenance_request = request.env['maintenance.request'].sudo().create(vals)
        if maintenance_request:
            maintenance_request.tenant_id = tenant_id
            if 'image' in post and post['image'].filename:
                file_data = post['image'].read()
                request.env['ir.attachment'].sudo().create({
                    'name': post['image'].filename,
                    'res_model': 'maintenance.request',
                    'res_id': maintenance_request.id,
                    'type': 'binary',
                    'datas': base64.b64encode(file_data),
                })
            res = maintenance_request
            message_body = f"""
                    Your service request has been registered successfully and our
                    service center being notified about it as well. You can expect the technician's
                    call within short time as per the priority, , 
                    Detail of Service Request: , 
                    Service Request No : {res.ticket_no}, 
                    Tenant Name : {res.tenant_id.name}, 
                    Contact Mobile : {res.tenant_id.mobile}, 
                    Contact Email : {res.tenant_id.email}, 
                    Building/ Villa Name : {res.building}, 
                    Flat Number/ Villa Number : {res.flat}, 
                    Location/ Address : {res.address}, 
                    Type of Work : {res.work_type}, 
                    Problem : {res.problem}, 
                    Problem Descriptions : {res.name}, 
                    Property Managed by : {res.property},
                    Maintenance Type : {res.maintenance_type}
                    """
            res.message_post(body=message_body)
            # if not maintenance_request.ticket_no:
            #     maintenance_request.ticket_no = 'GCL-' + today.strftime('%Y') + '-' + str(maintenance_request.id)
            return request.redirect(f"/maintenance-request/thank-you/{maintenance_request.id}")


    @http.route('/maintenance-request/thank-you/<int:ticket_id>', type='http', website=True, auth='public')
    def maintenance_request_thankyou(self, ticket_id):
        ticket = request.env['maintenance.request'].sudo().browse(int(ticket_id))
        if ticket:
            return request.render("cpahelpdesk.ticket_welcome", {
                'ticket_no': ticket.ticket_no,
                'building': ticket.building,
                'flat': ticket.flat,
                'work_type': ticket.work_type,
                'problem': ticket.problem,
                'problem_detail': ticket.name,
                'property': ticket.property,
                'tenant': ticket.tenant_id.name,
                'mobile': ticket.tenant_id.mobile,
                'email': ticket.tenant_id.email,
                'address': ticket.address,
                'maintenance_type': ticket.maintenance_type,
            })
