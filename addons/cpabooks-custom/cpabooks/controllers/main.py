from odoo import http
from odoo.http import request

class CpaBook(http.Controller):

    @http.route('/web/signup', type='http', website=True, auth='public')
    def web_signup(self, **kw):
        return request.render("cpabooks.company_signup", {})

    @http.route('/create/partner/', type='http', website=True, auth='public')
    def create_partner(self, **kw):

        partner_val = {
            'name': kw.get('name'),
            'display_name': kw.get('name'),
            'type': 'contact',
            'phone': kw.get('phone'),
            'active': True,
            'email': kw.get('email'),
            'is_company': True,
            'commercial_company_name': kw.get('company'),
            'company_name': kw.get('company')

        }

        #request.env['res.partner'].sudo().create(partner_val)
        res_id: any = request.env['res.partner'].sudo().create(partner_val)

        company_val = {
            'name': kw.get('company'),
            'phone': kw.get('phone'),
            'email': kw.get('email'),
            'transfer_account_id': 1,
            'chart_template_id': 1,
            'bank_account_code_prefix': '1014',
            'cash_account_code_prefix': '1015',
            'default_cash_difference_expense_account_id': 32,
            'partner_id': int(res_id[0].id)
        }
       
        print("My ID:", int(res_id[0].id))

        company_id: any = request.env['res.company'].sudo().create(company_val)

        user_value = {
            'login': kw.get('email'),
            'password': kw.get('password'),
            'active': True,
            'partner_id': int(res_id[0].id),
            'company_id': 1
        }
        
        #int(company_id[0].id)
        
        request.env['res.users'].sudo().create(user_value)
        #print("My ID:", res_id+company_id)

        return request.render("cpabooks.company_welcome", {})
