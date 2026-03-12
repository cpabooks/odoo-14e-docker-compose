import base64
import csv
import io

from odoo import models, fields, api, modules,_
from odoo.exceptions import ValidationError

class VisaProductShow(models.TransientModel):
    _name="visa.product.show"

    visa_product_show_id=fields.Many2one('product.analytic.acc.conf')
    visa_product=fields.Char(string="Visa Product")
    expense_ledger_id=fields.Many2one('account.account',string="Expense Ledger", default=lambda self:self.env['account.account'].sudo().search([('name','=ilike','prepaid visa expenses%'),('company_id','=',self.env.company.id)],limit=1))
    company_id = fields.Many2one('res.company')
    item_id = fields.Many2one('product.template', string="Item Name")


class VisaProduct(models.Model):
    _name = "visa.product"

    visa_product_id = fields.Many2one('product.analytic.acc.conf')
    visa_product = fields.Char(string="Visa Product")
    expense_ledger_id=fields.Many2one('account.account',string="Expense Ledger", default=lambda self:self.env['account.account'].sudo().search([('name','=ilike','prepaid visa expenses%'),('company_id','=',self.env.company.id)],limit=1))
    company_id = fields.Many2one('res.company')
    item_id = fields.Many2one('product.template', string="Item Name")

    @api.model
    def action_create_default_visa_product(self):
        val_list = []
        visa_product_val = []
        get_all_company = self.env['res.company'].sudo().search([])
        all_create_product = self.env['product.template']
        for com in get_all_company:
            # get_visa_expense_id=self.env['account.account'].sudo().search([('name','=ilike',"prepaid visa expenses%")],limit=1)
            if not self.env['product.template'].sudo().search(
                    [('name', '=ilike', '%Visa - Visa Application Fee%'), ('company_id', '=', com.id)]):
                create_product = self.env['product.template'].sudo().create({
                    'name': "Visa - Visa Application Fee",
                    'type': 'product',
                    'sale_ok': True,
                    'purchase_ok': True,
                    'categ_id': self.env['product.category'].sudo().search([('name', '=', 'All')], limit=1).id,
                    'uom_id': self.env['uom.uom'].sudo().search([('name', '=ilike', 'Unit%')], limit=1).id,
                    'uom_po_id': self.env['uom.uom'].sudo().search([('name', '=ilike', 'Unit%')], limit=1).id,
                    'purchase_line_warn': "no-message",
                    'company_id': com.id
                })
                all_create_product += create_product
                visa_product_val.append({
                    "visa_product": "Visa - Visa Application Fee",
                    "company_id": com.id,
                    "item_id": create_product.id
                })
            else:
                check_exists_in_visa_pro_table=self.env['visa.product'].sudo().search([('item_id.name', '=ilike', '%Visa - Visa Application Fee%'),
                                                                                       ('company_id', '=', com.id)],limit=1)
                if not check_exists_in_visa_pro_table:
                    get_product=self.env['product.template'].sudo().search(
                    [('name', '=ilike', '%Visa - Visa Application Fee%'), ('company_id', '=', com.id)])
                    visa_product_val.append({
                        "visa_product": "Visa - Visa Application Fee",
                        "company_id": com.id,
                        "item_id": get_product.id
                    })

            if not self.env['product.template'].sudo().search(
                    [('name', '=ilike', '%Visa - Security Deposit%'), ('company_id', '=', com.id)]):
                create_product = self.env['product.template'].sudo().create({
                    'name': "Visa - Security Deposit",
                    'type': 'product',
                    'sale_ok': True,
                    'purchase_ok': True,
                    'categ_id': self.env['product.category'].sudo().search([('name', '=', 'All')], limit=1).id,
                    'uom_id': self.env['uom.uom'].sudo().search([('name', '=ilike', 'Unit%')], limit=1).id,
                    'uom_po_id': self.env['uom.uom'].sudo().search([('name', '=ilike', 'Unit%')], limit=1).id,
                    'company_id': com.id
                    # 'purchase_line_warn': "no-message"
                })
                all_create_product += create_product
                visa_product_val.append({
                    "visa_product": "Visa - Security Deposit",
                    "company_id": com.id,
                    "item_id": create_product.id
                })
            else:
                check_exists_in_visa_pro_table = self.env['visa.product'].sudo().search(
                    [('item_id.name', '=ilike', '%Visa - Security Deposit%'),
                     ('company_id', '=', com.id)], limit=1)
                if not check_exists_in_visa_pro_table:
                    get_product = self.env['product.template'].sudo().search(
                        [('name', '=ilike', '%Visa - Security Deposit%'), ('company_id', '=', com.id)])
                    visa_product_val.append({
                        "visa_product": "Visa - Security Deposit",
                        "company_id": com.id,
                        "item_id": get_product.id
                    })
            if not self.env['product.template'].sudo().search(
                    [('name', '=ilike', '%Visa - Medical Examination Fee%'), ('company_id', '=', com.id)]):
                create_product = self.env['product.template'].sudo().create({
                    'name': "Visa - Medical Examination Fee",
                    'type': 'product',
                    'sale_ok': True,
                    'purchase_ok': True,
                    'categ_id': self.env['product.category'].sudo().search([('name', '=', 'All')], limit=1).id,
                    'uom_id': self.env['uom.uom'].sudo().search([('name', '=ilike', 'Unit%')], limit=1).id,
                    'uom_po_id': self.env['uom.uom'].sudo().search([('name', '=ilike', 'Unit%')], limit=1).id,
                    'company_id': com.id
                    # 'purchase_line_warn': "no-message"
                })
                all_create_product += create_product
                visa_product_val.append({
                    "visa_product": "Visa - Medical Examination Fee",
                    "company_id": com.id,
                    "item_id": create_product.id
                })
            else:
                check_exists_in_visa_pro_table = self.env['visa.product'].sudo().search(
                    [('item_id.name', '=ilike', '%Visa - Medical Examination Fee%'),
                     ('company_id', '=', com.id)], limit=1)
                if not check_exists_in_visa_pro_table:
                    get_product = self.env['product.template'].sudo().search(
                        [('name', '=ilike', '%Visa - Medical Examination Fee%'), ('company_id', '=', com.id)])
                    visa_product_val.append({
                        "visa_product": "Visa - Medical Examination Fee",
                        "company_id": com.id,
                        "item_id": get_product.id
                    })
            if not self.env['product.template'].sudo().search(
                    [('name', '=ilike', '%Visa - Emirates ID Card Fee%'), ('company_id', '=', com.id)]):
                create_product = self.env['product.template'].sudo().create({
                    'name': "Visa - Emirates ID Card Fee",
                    'type': 'product',
                    'sale_ok': True,
                    'purchase_ok': True,
                    'categ_id': self.env['product.category'].sudo().search([('name', '=', 'All')], limit=1).id,
                    'uom_id': self.env['uom.uom'].sudo().search([('name', '=ilike', 'Unit%')], limit=1).id,
                    'uom_po_id': self.env['uom.uom'].sudo().search([('name', '=ilike', 'Unit%')], limit=1).id,
                    'company_id': com.id
                    # 'purchase_line_warn': "no-message"
                })
                all_create_product += create_product
                visa_product_val.append({
                    "visa_product": "Visa - Emirates ID Card Fee",
                    "company_id": com.id,
                    "item_id": create_product.id
                })
            else:
                check_exists_in_visa_pro_table = self.env['visa.product'].sudo().search(
                    [('item_id.name', '=ilike', '%Visa - Emirates ID Card Fee%'),
                     ('company_id', '=', com.id)], limit=1)
                if not check_exists_in_visa_pro_table:
                    get_product = self.env['product.template'].sudo().search(
                        [('name', '=ilike', '%Visa - Emirates ID Card Fee%'), ('company_id', '=', com.id)])
                    visa_product_val.append({
                        "visa_product": "Visa - Emirates ID Card Fee",
                        "company_id": com.id,
                        "item_id": get_product.id
                    })
            if not self.env['product.template'].sudo().search(
                    [('name', '=ilike', '%Visa - Insurance Fee%'), ('company_id', '=', com.id)]):
                create_product = self.env['product.template'].sudo().create({
                    'name': "Visa - Insurance Fee",
                    'type': 'product',
                    'sale_ok': True,
                    'purchase_ok': True,
                    'categ_id': self.env['product.category'].sudo().search([('name', '=', 'All')], limit=1).id,
                    'uom_id': self.env['uom.uom'].sudo().search([('name', '=ilike', 'Unit%')], limit=1).id,
                    'uom_po_id': self.env['uom.uom'].sudo().search([('name', '=ilike', 'Unit%')], limit=1).id,
                    'company_id': com.id
                    # 'purchase_line_warn': "no-message"
                })
                all_create_product += create_product
                visa_product_val.append({
                    "visa_product": "Visa - Insurance Fee",
                    "company_id": com.id,
                    "item_id": create_product.id
                })
            else:
                check_exists_in_visa_pro_table = self.env['visa.product'].sudo().search(
                    [('item_id.name', '=ilike', '%Visa - Insurance Fee%'),
                     ('company_id', '=', com.id)], limit=1)
                if not check_exists_in_visa_pro_table:
                    get_product = self.env['product.template'].sudo().search(
                        [('name', '=ilike', '%Visa - Insurance Fee%'), ('company_id', '=', com.id)])
                    visa_product_val.append({
                        "visa_product": "Visa - Insurance Fee",
                        "company_id": com.id,
                        "item_id": get_product.id
                    })
            if not self.env['product.template'].sudo().search(
                    [('name', '=ilike', '%Visa - Typing Centers Fee%'), ('company_id', '=', com.id)]):
                create_product = self.env['product.template'].sudo().create({
                    'name': "Visa - Typing Centers Fee",
                    'type': 'product',
                    'sale_ok': True,
                    'purchase_ok': True,
                    'categ_id': self.env['product.category'].sudo().search([('name', '=', 'All')], limit=1).id,
                    'uom_id': self.env['uom.uom'].sudo().search([('name', '=ilike', 'Unit%')], limit=1).id,
                    'uom_po_id': self.env['uom.uom'].sudo().search([('name', '=ilike', 'Unit%')], limit=1).id,
                    'company_id': com.id
                    # 'purchase_line_warn': "no-message"
                })
                all_create_product += create_product
                visa_product_val.append({
                    "visa_product": "Visa - Typing Centers Fee",
                    "company_id": com.id,
                    "item_id": create_product.id

                })
            else:
                check_exists_in_visa_pro_table = self.env['visa.product'].sudo().search(
                    [('item_id.name', '=ilike', '%Visa - Typing Centers Fee%'),
                     ('company_id', '=', com.id)], limit=1)
                if not check_exists_in_visa_pro_table:
                    get_product = self.env['product.template'].sudo().search(
                        [('name', '=ilike', '%Visa - Typing Centers Fee%'), ('company_id', '=', com.id)])
                    visa_product_val.append({
                        "visa_product": "Visa - Typing Centers Fee",
                        "company_id": com.id,
                        "item_id": get_product.id
                    })
            if not self.env['product.template'].sudo().search(
                    [('name', '=ilike', '%Visa - Express or Urgent Processing Fee%'), ('company_id', '=', com.id)]):
                create_product = self.env['product.template'].sudo().create({
                    'name': "Visa - Express or Urgent Processing Fee",
                    'type': 'product',
                    'sale_ok': True,
                    'purchase_ok': True,
                    'categ_id': self.env['product.category'].sudo().search([('name', '=', 'All')], limit=1).id,
                    'uom_id': self.env['uom.uom'].sudo().search([('name', '=ilike', 'Unit%')], limit=1).id,
                    'uom_po_id': self.env['uom.uom'].sudo().search([('name', '=ilike', 'Unit%')], limit=1).id,
                    'company_id': com.id
                    # 'purchase_line_warn': "no-message"
                })
                all_create_product += create_product
                visa_product_val.append({
                    "visa_product": "Visa - Express or Urgent Processing Fee",
                    "company_id": com.id,
                    "item_id": create_product.id
                })
            else:
                check_exists_in_visa_pro_table = self.env['visa.product'].sudo().search(
                    [('item_id.name', '=ilike', '%Visa - Express or Urgent Processing Fee%'),
                     ('company_id', '=', com.id)], limit=1)
                if not check_exists_in_visa_pro_table:
                    get_product = self.env['product.template'].sudo().search(
                        [('name', '=ilike', '%Visa - Express or Urgent Processing Fee%'), ('company_id', '=', com.id)])
                    visa_product_val.append({
                        "visa_product": "Visa - Express or Urgent Processing Fee",
                        "company_id": com.id,
                        "item_id": get_product.id
                    })
            if not self.env['product.template'].sudo().search(
                    [('name', '=ilike', '%Visa - Change of Status Fee%'), ('company_id', '=', com.id)]):
                create_product = self.env['product.template'].sudo().create({
                    'name': "Visa - Change of Status Fee",
                    'type': 'product',
                    'sale_ok': True,
                    'purchase_ok': True,
                    'categ_id': self.env['product.category'].sudo().search([('name', '=', 'All')], limit=1).id,
                    'uom_id': self.env['uom.uom'].sudo().search([('name', '=ilike', 'Unit%')], limit=1).id,
                    'uom_po_id': self.env['uom.uom'].sudo().search([('name', '=ilike', 'Unit%')], limit=1).id,
                    'company_id': com.id
                    # 'purchase_line_warn': "no-message"
                })
                all_create_product += create_product
                visa_product_val.append({
                    "visa_product": "Visa - Change of Status Fee",
                    "company_id": com.id,
                    "item_id": create_product.id
                })
            else:
                check_exists_in_visa_pro_table = self.env['visa.product'].sudo().search(
                    [('item_id.name', '=ilike', '%Visa - Change of Status Fee%'),
                     ('company_id', '=', com.id)], limit=1)
                if not check_exists_in_visa_pro_table:
                    get_product = self.env['product.template'].sudo().search(
                        [('name', '=ilike', '%Visa - Change of Status Fee%'), ('company_id', '=', com.id)])
                    visa_product_val.append({
                        "visa_product": "Visa - Change of Status Fee",
                        "company_id": com.id,
                        "item_id": get_product.id
                    })
            if not self.env['product.template'].sudo().search(
                    [('name', '=ilike', '%Visa - Overstay Fine%'), ('company_id', '=', com.id)]):
                create_product = self.env['product.template'].sudo().create({
                    'name': "Visa - Overstay Fine",
                    'type': 'product',
                    'sale_ok': True,
                    'purchase_ok': True,
                    'categ_id': self.env['product.category'].sudo().search([('name', '=', 'All')], limit=1).id,
                    'uom_id': self.env['uom.uom'].sudo().search([('name', '=ilike', 'Unit%')], limit=1).id,
                    'uom_po_id': self.env['uom.uom'].sudo().search([('name', '=ilike', 'Unit%')], limit=1).id,
                    'company_id': com.id
                    # 'purchase_line_warn': "no-message"
                })
                all_create_product += create_product
                visa_product_val.append({
                    "visa_product": "Visa - Overstay Fine",
                    "company_id": com.id,
                    "item_id": create_product.id
                })
            else:
                check_exists_in_visa_pro_table = self.env['visa.product'].sudo().search(
                    [('item_id.name', '=ilike', '%Visa - Overstay Fine%'),
                     ('company_id', '=', com.id)], limit=1)
                if not check_exists_in_visa_pro_table:
                    get_product = self.env['product.template'].sudo().search(
                        [('name', '=ilike', '%Visa - Overstay Fine%'), ('company_id', '=', com.id)])
                    visa_product_val.append({
                        "visa_product": "Visa - Overstay Fine",
                        "company_id": com.id,
                        "item_id": get_product.id
                    })
            if not self.env['product.template'].sudo().search(
                    [('name', '=ilike', '%Visa - Visa Renewal Fee%'), ('company_id', '=', com.id)]):
                create_product = self.env['product.template'].sudo().create({
                    'name': "Visa - Visa Renewal Fee",
                    'type': 'product',
                    'sale_ok': True,
                    'purchase_ok': True,
                    'categ_id': self.env['product.category'].sudo().search([('name', '=', 'All')], limit=1).id,
                    'uom_id': self.env['uom.uom'].sudo().search([('name', '=ilike', 'Unit%')], limit=1).id,
                    'uom_po_id': self.env['uom.uom'].sudo().search([('name', '=ilike', 'Unit%')], limit=1).id,
                    'company_id': com.id
                    # 'purchase_line_warn': "no-message"
                })
                all_create_product += create_product
                visa_product_val.append({
                    "visa_product": "Visa - Visa Renewal Fee",
                    "company_id": com.id,
                    "item_id": create_product.id
                })
            else:
                check_exists_in_visa_pro_table = self.env['visa.product'].sudo().search(
                    [('item_id.name', '=ilike', '%Visa - Visa Renewal Fee%'),
                     ('company_id', '=', com.id)], limit=1)
                if not check_exists_in_visa_pro_table:
                    get_product = self.env['product.template'].sudo().search(
                        [('name', '=ilike', '%Visa - Visa Renewal Fee%'), ('company_id', '=', com.id)])
                    visa_product_val.append({
                        "visa_product": "Visa - Visa Renewal Fee",
                        "company_id": com.id,
                        "item_id": get_product.id
                    })
            if not self.env['product.template'].sudo().search(
                    [('name', '=ilike', '%Visa - Others%'), ('company_id', '=', self.env.company.id)]):
                create_product = self.env['product.template'].sudo().create({
                    'name': "Visa - Others",
                    'type': 'product',
                    'sale_ok': True,
                    'purchase_ok': True,
                    'categ_id': self.env['product.category'].sudo().search([('name', '=', 'All')], limit=1).id,
                    'uom_id': self.env['uom.uom'].sudo().search([('name', '=ilike', 'Unit%')], limit=1).id,
                    'uom_po_id': self.env['uom.uom'].sudo().search([('name', '=ilike', 'Unit%')], limit=1).id,
                    "company_id": com.id
                    # 'purchase_line_warn': "no-message"
                })
                all_create_product += create_product
                visa_product_val.append({
                    "visa_product": "Visa - Others",
                    "company_id": com.id,
                    "item_id": create_product.id
                })
            else:
                check_exists_in_visa_pro_table = self.env['visa.product'].sudo().search(
                    [('item_id.name', '=ilike', '%Visa - Others%'),
                     ('company_id', '=', com.id)], limit=1)
                if not check_exists_in_visa_pro_table:
                    get_product = self.env['product.template'].sudo().search(
                        [('name', '=ilike', '%Visa - Others%'), ('company_id', '=', com.id)])
                    visa_product_val.append({
                        "visa_product": "Visa - Others",
                        "company_id": com.id,
                        "item_id": get_product.id
                    })

        # if val_list:
        #     create_product=self.env['product.template'].sudo().create(val_list)
        if visa_product_val:
            create_visa_product = self.env['visa.product'].sudo().create(visa_product_val)
        all_company = self.env['res.company'].sudo().search([])
        for com in all_company:
            get_company_prepaid_visa_expense_id = self.env['account.account'].sudo().search(
                [('name', '=ilike', 'prepaid visa expenses%'), ('company_id', '=', com.id)], limit=1)
            if get_company_prepaid_visa_expense_id:
                for pro in all_create_product:
                    pro.with_company(com.id).sudo().write(
                        {'property_account_expense_id': get_company_prepaid_visa_expense_id.id})
            else:
                # get_field_exist=self.env['ir.model.fields'].sudo().search([('name','=','create_asset'),('model_id','=',self.env['ir.model'].sudo().search([('model','=','account.account')]).id)])
                # if get_field_exist:
                get_company_prepaid_visa_expense_id = self.env['account.account'].sudo().create({
                    'name': 'Prepaid Visa Expenses',
                    'code': '565006PVE',
                    'company_id': com.id,
                    'user_type_id': self.env['account.account.type'].sudo().search([('name', '=', 'Expenses')]).id,

                })
                # else:
                #     get_company_prepaid_visa_expense_id = self.env['account.account'].sudo().create({
                #         'name': 'Prepaid Visa Expenses',
                #         'code': '565006PVE',
                #         'company_id': com.id,
                #         'user_type_id': self.env['account.account.type'].sudo().search([('name', '=', 'Expenses')]).id,
                #     })
                for pro in all_create_product:
                    pro.with_company(com.id).sudo().write(
                        {'property_account_expense_id': get_company_prepaid_visa_expense_id.id})
                # raise ValidationError(_("Company "+com.name+" have no Prepaid Visa Expenses account\nPlease create (Prepaid Visa Expenses) ledger first for your company"))

    @api.model
    def action_attach_existing_vehicle_product(self):
        get_all_company = self.env['res.company'].sudo().search([])
        val_list=[]
        for com in get_all_company:
            get_all_vehicle_related_product=self.env['product.product'].sudo().search([('name','=ilike',"Vehicle Fuel Exp # %"),('company_id','=',com.id)])
            get_all_vehicle_related_product+=self.env['product.product'].sudo().search([('name','=ilike',"Vehicle Maint. # %"),('company_id','=',com.id)])
            get_all_vehicle_setup=self.env['product.analytic.acc.conf.line'].search([('company_id','=',com.id)])
            for product in get_all_vehicle_related_product:
                if product.id not in get_all_vehicle_setup.item_id.ids:
                    v_no=product.name.split("#")[1]
                    get_analytic_acc=self.env['account.analytic.account'].sudo().search([('name','=',product.name),('company_id','=',com.id)],limit=1)
                    val_list.append({
                        'vehicle_no': v_no.strip(),
                        'item_id':  product.id,
                        'analytic_acc_id':get_analytic_acc.id if get_analytic_acc else None,
                        'analytic_group_id': get_analytic_acc.group_id.id if get_analytic_acc else None,
                        'company_id': com.id,
                        'expense_ledger_id':product.product_tmpl_id.with_company(com.id).property_account_expense_id.id
                    })
        if val_list:
            self.env['product.analytic.acc.conf.line'].sudo().create(val_list)


    @api.model
    def action_attach_existing_visa_analytic_acc(self):
        get_all_company = self.env['res.company'].sudo().search([])
        val_list = []
        for com in get_all_company:
            get_all_emp=self.env['hr.employee'].sudo().search([('company_id','=',com.id)])
            for emp in get_all_emp:
                get_analytic_acc=self.env['account.analytic.account'].sudo().search([('company_id','=',com.id),('name','=ilike','Visa - '+emp.name+'%')],limit=1)
                if get_analytic_acc and not self.env['visa.analytic.acc'].sudo().search([('analytic_acc_id','=',get_analytic_acc.id)]):
                    val_list.append({
                        'analytic_acc_id': get_analytic_acc.id,
                        'analytic_group_id': get_analytic_acc.group_id.id,
                        'company_id': com.id
                    })
        if val_list:
            self.env['visa.analytic.acc'].sudo().create(val_list)

class VisaAnalyticAcc(models.Model):
    _name = "visa.analytic.acc"

    visa_ana_acc_id = fields.Many2one('product.analytic.acc.conf')
    analytic_acc_id=fields.Many2one('account.analytic.account',string="Analytical Account")
    company_id = fields.Many2one('res.company')
    analytic_group_id = fields.Many2one('account.analytic.group', string="Analytical Group")



