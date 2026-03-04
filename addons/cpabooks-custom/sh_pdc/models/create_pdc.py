from odoo import api, models, _
from odoo.exceptions import ValidationError


class CreatePDCAccount(models.Model):
    _name = 'create.pdc.account'

    @api.model
    def action_create_pdc(self):
        get_all_company=self.env['res.company'].sudo().search([])

        val_list = []
        for com in get_all_company:
            search_pdc_acc=self.env['account.account'].search([('code','in',('100012','100011')),('company_id','=',com.id)])

            if not search_pdc_acc:
                # payable_user_type_id = self.env['account.account.type'].sudo().search([('name', '=', 'Payable')]).id
                # query="""insert into account_account (name,code,user_type_id,reconcile,company_id,create_asset)
                # values ('PDC Payable','100012',{},True,{},'no')""".format(payable_user_type_id,com.id)
                # self._cr.execute(query=query)
                #
                # receivable_user_type_id = self.env['account.account.type'].sudo().search([('name', '=', 'Receivable')]).id
                # query = """insert into account_account (name,code,user_type_id,reconcile,company_id,create_asset)
                #                 values ('PDC Receivable','100011',{},True,{},'no')""".format(receivable_user_type_id, com.id)
                # self._cr.execute(query=query)
                vals1={
                    'name':'PDC Payable',
                    'code':'100012',
                    'user_type_id':self.env['account.account.type'].sudo().search([('name','=','Payable')]).id,
                    'reconcile':True,
                    'company_id':com.id
                }
                val_list.append(vals1)

                vals2 = {
                    'name': 'PDC Receivable',
                    'code': '100011',
                    'user_type_id': self.env['account.account.type'].sudo().search([('name', '=', 'Receivable')]).id,
                    'reconcile': True,
                    'company_id': com.id
                }
                val_list.append(vals2)
        if len(val_list)>0:
            self.env['account.account'].sudo().create(val_list)
        for com in get_all_company:

                query = "UPDATE res_company SET pdc_customer=(select id from account_account where name ilike 'PDC Receivable' and company_id={}) " \
                        "where id={};" \
                        "UPDATE res_company SET pdc_vendor=(select id from account_account where name ilike 'PDC Payable' and company_id={})" \
                        "where id={};".format(com.id,com.id,com.id,com.id)
                self._cr.execute(query)




