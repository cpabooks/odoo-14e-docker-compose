from odoo import fields, models, api
from odoo.exceptions import ValidationError

ACCOUNT_DOMAIN = "['&', '&', '&', ('deprecated', '=', False), ('internal_type','=','other'), ('company_id', '=', current_company_id), ('is_off_balance', '=', False)]"

class ProductCategoryInherit(models.Model):
    _inherit = "product.category"

    parent_id = fields.Many2one('product.category', 'Parent Category', index=True, ondelete='cascade', default=lambda self:self.env['product.category'].search([('name','=ilike','all')]).id)
    property_valuation = fields.Selection([
        ('manual_periodic', 'Manual'),
        ('real_time', 'Automated')], string='Inventory Valuation',
        company_dependent=True, copy=True, required=True,default='real_time',
        help="""Manual: The accounting entries to value the inventory are not posted automatically.
            Automated: An accounting entry is automatically created to value the inventory when a product enters or leaves the company.
            """)
    removal_strategy_id = fields.Many2one(
        'product.removal', 'Force Removal Strategy',default=lambda self:self.env['product.removal'].search([('name','=ilike','%FIFO%')]).id,
        help="Set a specific removal strategy that will be used regardless of the source location for this product category")
    property_stock_valuation_account_id = fields.Many2one(
        'account.account', 'Stock Valuation Account', company_dependent=True,
        domain="[('company_id', '=', allowed_company_ids[0]), ('deprecated', '=', False)]", check_company=True,
        help="""When automated inventory valuation is enabled on a product, this account will hold the current value of the products.""",
        default= lambda self:self.env['account.account'].sudo().search([('name','ilike','Stock Valuation Account%'),('company_id','=',self.env.company.id )],limit=1).id)

    property_stock_account_input_categ_id = fields.Many2one(
        'account.account', 'Stock Input Account', company_dependent=True,
        domain="[('company_id', '=', allowed_company_ids[0]), ('deprecated', '=', False)]", check_company=True,
        help="""Counterpart journal items for all incoming stock moves will be posted in this account, unless there is a specific valuation account
                   set on the source location. This is the default value for all products in this category. It can also directly be set on each product.""",
        default= lambda self:self.env['account.account'].sudo().search([('name','ilike','Stock Input Account (cos)%'),('company_id','=',self.env.company.id)],limit=1).id)

    property_stock_account_output_categ_id = fields.Many2one(
        'account.account', 'Stock Output Account', company_dependent=True,
        domain="[('company_id', '=', allowed_company_ids[0]), ('deprecated', '=', False)]", check_company=True,
        help="""When doing automated inventory valuation, counterpart journal items for all outgoing stock moves will be posted in this account,
                  unless there is a specific valuation account set on the destination location. This is the default value for all products in this category.
                  It can also directly be set on each product.""",
        default= lambda self:self.env['account.account'].sudo().search([('name','ilike','Stock Output Account (cos)%'),('company_id','=',self.env.company.id)],limit=1).id)

    property_account_income_categ_id = fields.Many2one('account.account', company_dependent=True,
                                                       string="Income Account",
                                                       domain=ACCOUNT_DOMAIN,
                                                       help="This account will be used when validating a customer invoice.",
                                                       default= lambda self:self.env['account.account'].sudo().search([('name','ilike','Sales Account%'),('company_id','=',self.env.company.id)]).id)
    property_account_expense_categ_id = fields.Many2one('account.account', company_dependent=True,
                                                        string="Expense Account",
                                                        domain=ACCOUNT_DOMAIN,
                                                        default=lambda self: self.env['account.account'].sudo().search(
                                                            [('name', 'ilike', 'Cost of Goods Sold in Trading%'),
                                                             ('company_id', '=', self.env.company.id)],limit=1).id,
                                                        help="The expense is accounted for when a vendor bill is validated, except in anglo-saxon accounting with perpetual inventory valuation in which case the expense (Cost of Goods Sold account) is recognized at the customer invoice validation.")

    property_stock_journal = fields.Many2one(
        'account.journal', 'Stock Journal', company_dependent=True,
        domain="[('company_id', '=', allowed_company_ids[0])]", check_company=True,
        default=lambda self: self.env['account.journal'].search(
                        [('name', 'ilike', 'Inventory Valuation%'), ('company_id', '=', self.env.company.id)],limit=1).id,
        help="When doing automated inventory valuation, this is the Accounting Journal in which entries will be automatically posted when stock moves are processed.")

    @api.model
    @api.model
    def update_product_category_fields(self):
        #IDENTITY GIVE 501 TO UP
        get_company = self.env['res.company'].sudo().search([])
        for com in get_company:
            val_list = []
            get_property_stock_valuation_account_id = self.env['account.account'].sudo().search(
                [('name', 'ilike', 'Stock Valuation Account%'), ('company_id', '=', com.id)],limit=1)

            if not get_property_stock_valuation_account_id:
                # raise ValidationError(com.name+" need to create chart of account first")
                vals = {
                    'code': '125050',
                    'name': 'Stock Valuation Account',
                    'user_type_id': self.env['account.account.type'].search([('name', '=ilike', '%current assets%')],
                                                                            limit=1).id,
                    'company_id': com.id,
                    'create_uid': self.env.user.id,
                    'identity_id': 501
                }

                val_list.append(vals)

            get_property_stock_account_input_categ_id = self.env['account.account'].search(
                [('name', 'ilike', 'Stock Input Account (cos)%'), ('company_id', '=', com.id)],limit=1)
            if not get_property_stock_account_input_categ_id:
                vals = {
                    'code': '580430',
                    'name': 'Stock Input Account (cos)',
                    'user_type_id': self.env['account.account.type'].search([('name', '=ilike', '%current assets%')],
                                                                            limit=1).id,
                    'company_id': com.id,
                    'create_uid': self.env.user.id,
                    'identity_id': 502
                }

                val_list.append(vals)
            get_property_stock_account_output_categ_id = self.env['account.account'].search(
                [('name', 'ilike', 'Stock Output Account (cos)%'), ('company_id', '=', com.id)],limit=1)
            if not get_property_stock_account_output_categ_id:
                vals = {
                    'code': '580435',
                    'name': 'Stock Output Account (cos)',
                    'user_type_id': self.env['account.account.type'].search([('name', '=ilike', '%current assets%')],
                                                                            limit=1).id,
                    'company_id': com.id,
                    'create_uid': self.env.user.id,
                    'identity_id': 503
                }
                val_list.append(vals)

            get_income_account = self.env['account.account'].sudo().search(
                [('name', 'ilike', 'Sales Account%'), ('company_id', '=', com.id)],limit=1)

            if not get_income_account:
                # raise ValidationError(com.name+" need to create chart of account first")
                vals = {
                    'code': '475370',
                    'name': 'Sales Account',
                    'user_type_id': self.env['account.account.type'].search([('name', '=ilike', '%income%')],
                                                                            limit=1).id,
                    'company_id': com.id,
                    'create_uid': self.env.user.id,
                    'identity_id': 504
                }

                val_list.append(vals)

            get_expense_account = self.env['account.account'].sudo().search(
                [('name', 'ilike', 'Cost of Goods Sold in Trading%'), ('company_id', '=', com.id)],limit=1)

            if not get_expense_account:
                # raise ValidationError(com.name+" need to create chart of account first")
                vals = {
                    'code': '580385',
                    'name': 'Cost of Goods Sold in Trading',
                    'user_type_id': self.env['account.account.type'].search([('name', '=ilike', '%Cost of Revenue%')],
                                                                            limit=1).id,
                    'company_id': com.id,
                    'create_uid': self.env.user.id,
                    'identity_id': 505
                }

                val_list.append(vals)
            if len(val_list) > 0:
                data = self.env['account.account'].sudo().create(val_list)

        # get_all_category=self.env['product.category'].search([('name','not ilike','all')],order="id asc")
        get_all_category = self.env['product.category'].search([])
        for rec in get_all_category:
            if rec.name != 'All':
                rec.parent_id = self.env['product.category'].search([('name', '=ilike', 'all')]).id
            rec.removal_strategy_id = self.env['product.removal'].search([('name', '=ilike', '%FIFO%')]).id
            get_company = self.env['res.company'].sudo().search([])
            val_ir_property = []
            for com in get_company:
                query = """delete from ir_property where res_id='{}' and name='{}' and company_id={}""".format(
                    'product.category,' + str(rec.id), 'property_cost_method', com.id)
                self._cr.execute(query=query)

                val = {
                    'name': "property_cost_method",
                    'res_id': 'product.category,' + str(rec.id),
                    'company_id': com.id,
                    'fields_id': self.env['ir.model.fields'].search(
                        [('name', '=', 'property_cost_method'), ('model', '=', 'product.category')]).id,
                    'value_text': 'standard',
                    'type': 'selection'
                }
                val_ir_property.append(val)

                query = """delete from ir_property where res_id='{}' and name='{}' and company_id={}""".format(
                    'product.category,' + str(rec.id), 'property_valuation', com.id)
                self._cr.execute(query=query)

                val = {
                    'name': "property_valuation",
                    'res_id': 'product.category,' + str(rec.id),
                    'company_id': com.id,
                    'fields_id': self.env['ir.model.fields'].search(
                        [('name', '=', 'property_valuation'), ('model', '=', 'product.category')]).id,
                    'value_text': 'real_time',
                    'type': 'selection'
                }
                val_ir_property.append(val)

                query = """delete from ir_property where res_id='{}' and name='{}' and company_id={}""".format(
                    'product.category,' + str(rec.id), 'property_stock_valuation_account_id', com.id)
                self._cr.execute(query=query)

                val = {
                    'name': "property_stock_valuation_account_id",
                    'res_id': 'product.category,' + str(rec.id),
                    'company_id': com.id,
                    'fields_id': self.env['ir.model.fields'].search(
                        [('name', '=', 'property_stock_valuation_account_id'), ('model', '=', 'product.category')]).id,
                    'value_reference': 'account.account,' + str(
                        self.env['account.account'].search([('name', 'ilike', 'Stock Valuation Account%'), ('company_id', '=', com.id)],limit=1).id),
                    'type': 'many2one'
                }
                val_ir_property.append(val)

                query = """delete from ir_property where res_id='{}' and name='{}' and company_id={}""".format(
                    'product.category,' + str(rec.id), 'property_stock_account_input_categ_id', com.id)
                self._cr.execute(query=query)

                val = {
                    'name': "property_stock_account_input_categ_id",
                    'res_id': 'product.category,' + str(rec.id),
                    'company_id': com.id,
                    'fields_id': self.env['ir.model.fields'].search(
                        [('name', '=', 'property_stock_account_input_categ_id'),
                         ('model', '=', 'product.category')]).id,
                    'value_reference': 'account.account,' + str(self.env['account.account'].search(
                        [('name', 'ilike', 'Stock Input Account (cos)%'), ('company_id', '=', com.id)],limit=1).id),
                    'type': 'many2one'
                }
                val_ir_property.append(val)

                query = """delete from ir_property where res_id='{}' and name='{}' and company_id={}""".format(
                    'product.category,' + str(rec.id), 'property_stock_account_output_categ_id', com.id)
                self._cr.execute(query=query)

                val = {
                    'name': "property_stock_account_output_categ_id",
                    'res_id': 'product.category,' + str(rec.id),
                    'company_id': com.id,
                    'fields_id': self.env['ir.model.fields'].search(
                        [('name', '=', 'property_stock_account_output_categ_id'),
                         ('model', '=', 'product.category')]).id,
                    'value_reference': 'account.account,' + str(self.env['account.account'].search(
                        [('name', 'ilike', 'Stock Output Account (cos)%'), ('company_id', '=', com.id)],limit=1).id),
                    'type': 'many2one'
                }
                val_ir_property.append(val)

                query = """delete from ir_property where res_id='{}' and name='{}' and company_id={}""".format(
                    'product.category,' + str(rec.id), 'property_account_income_categ_id', com.id)
                self._cr.execute(query=query)

                val = {
                    'name': "property_account_income_categ_id",
                    'res_id': 'product.category,' + str(rec.id),
                    'company_id': com.id,
                    'fields_id': self.env['ir.model.fields'].search(
                        [('name', '=', 'property_account_income_categ_id'),
                         ('model', '=', 'product.category')]).id,
                    'value_reference': 'account.account,' + str(self.env['account.account'].search(
                        [('name', 'ilike', 'Sales Account%'), ('company_id', '=', com.id)],limit=1).id),
                    'type': 'many2one'
                }

                val_ir_property.append(val)

                query = """delete from ir_property where res_id='{}' and name='{}' and company_id={}""".format(
                    'product.category,' + str(rec.id), 'property_account_expense_categ_id', com.id)
                self._cr.execute(query=query)

                val = {
                    'name': "property_account_expense_categ_id",
                    'res_id': 'product.category,' + str(rec.id),
                    'company_id': com.id,
                    'fields_id': self.env['ir.model.fields'].search(
                        [('name', '=', 'property_account_expense_categ_id'),
                         ('model', '=', 'product.category')]).id,
                    'value_reference': 'account.account,' + str(self.env['account.account'].search(
                        [('name', 'ilike', 'Cost of Goods Sold in Trading%'), ('company_id', '=', com.id)],limit=1).id),
                    'type': 'many2one'
                }

                query = """delete from ir_property where res_id='{}' and name='{}' and company_id={}""".format(
                    'product.category,' + str(rec.id), 'property_stock_journal', com.id)
                self._cr.execute(query=query)
                val_ir_property.append(val)

                val = {
                    'name': "property_stock_journal",
                    'res_id': 'product.category,' + str(rec.id),
                    'company_id': com.id,
                    'fields_id': self.env['ir.model.fields'].search(
                        [('name', '=', 'property_stock_journal'),
                         ('model', '=', 'product.category')]).id,
                    'value_reference': 'account.account,' + str(self.env['account.journal'].search(
                        [('name', 'ilike', '%Inventory Valuation%'), ('company_id', '=', com.id)],limit=1).id),
                    'type': 'many2one'
                }
                val_ir_property.append(val)

            self.env['ir.property'].sudo().create(val_ir_property)
            print('Executed update product category fields')

    # @api.model
    # def update_product_category_fields(self):
    #     get_company = self.env['res.company'].sudo().search([])
    #     for com in get_company:
    #         get_property_stock_valuation_account_id=self.env['account.account'].sudo().search([('name','',10),('company_id','=',com.id)])
    #         val_list=[]
    #         if not get_property_stock_valuation_account_id:
    #             # raise ValidationError(com.name+" need to create chart of account first")
    #             vals = {
    #                 'code': '125050',
    #                 'name': 'Stock Valuation Account',
    #                 'user_type_id': self.env['account.account.type'].search([('name', '=ilike', '%current assets%')],
    #                                                                         limit=1).id,
    #                 'company_id':com.id,
    #                 'create_uid': self.env.user.id,
    #                 'identity_id':10
    #             }
    #
    #             val_list.append(vals)
    #
    #         get_property_stock_account_input_categ_id = self.env['account.account'].search([('identity_id', '=', 88),('company_id','=',com.id)])
    #         if not get_property_stock_account_input_categ_id:
    #             vals = {
    #                 'code': '580430',
    #                 'name': 'Stock Input Account (cos)',
    #                 'user_type_id': self.env['account.account.type'].search([('name', '=ilike', '%current assets%')],
    #                                                                         limit=1).id,
    #                 'company_id': com.id,
    #                 'create_uid': self.env.user.id,
    #                 'identity_id':88
    #             }
    #
    #             val_list.append(vals)
    #         get_property_stock_account_output_categ_id = self.env['account.account'].search([('identity_id', '=', 89),('company_id','=',com.id)])
    #         if not get_property_stock_account_output_categ_id:
    #             vals = {
    #                 'code': '580435',
    #                 'name': 'Stock Output Account (cos)',
    #                 'user_type_id': self.env['account.account.type'].search([('name', '=ilike', '%current assets%')],
    #                                                                         limit=1).id,
    #                 'company_id': com.id,
    #                 'create_uid':self.env.user.id,
    #                 'identity_id':89
    #             }
    #             val_list.append(vals)
    #
    #         get_income_account = self.env['account.account'].sudo().search(
    #             [('identity_id', '=', 76), ('company_id', '=', com.id)])
    #         val_list = []
    #         if not get_income_account:
    #             # raise ValidationError(com.name+" need to create chart of account first")
    #             vals = {
    #                 'code': '475370',
    #                 'name': 'Sales Account',
    #                 'user_type_id': self.env['account.account.type'].search([('name', '=ilike', '%income%')],
    #                                                                         limit=1).id,
    #                 'company_id': com.id,
    #                 'create_uid': self.env.user.id,
    #                 'identity_id': 76
    #             }
    #
    #             val_list.append(vals)
    #
    #         get_expense_account = self.env['account.account'].sudo().search(
    #             [('identity_id', '=', 79), ('company_id', '=', com.id)])
    #         val_list = []
    #         if not get_expense_account:
    #             # raise ValidationError(com.name+" need to create chart of account first")
    #             vals = {
    #                 'code': '580385',
    #                 'name': 'Cost of Goods Sold in Trading',
    #                 'user_type_id': self.env['account.account.type'].search([('name', '=ilike', '%Cost of Revenue%')],
    #                                                                         limit=1).id,
    #                 'company_id': com.id,
    #                 'create_uid': self.env.user.id,
    #                 'identity_id': 79
    #             }
    #
    #             val_list.append(vals)
    #         if len(val_list)>0:
    #             data=self.env['account.account'].sudo().create(val_list)
    #     # get_all_category=self.env['product.category'].search([('name','not ilike','all')],order="id asc")
    #     get_all_category=self.env['product.category'].search([])
    #     for rec in get_all_category:
    #         if rec.name!='All':
    #             rec.parent_id=self.env['product.category'].search([('name','=ilike','all')]).id
    #         rec.removal_strategy_id = self.env['product.removal'].search([('name','=ilike','%FIFO%')]).id
    #         get_company=self.env['res.company'].sudo().search([])
    #         val_ir_property = []
    #         for com in get_company:
    #
    #             query="""delete from ir_property where res_id='{}' and name='{}' and company_id={}""".format('product.category,'+str(rec.id),'property_cost_method',com.id)
    #             self._cr.execute(query=query)
    #
    #             val={
    #                 'name': "property_cost_method",
    #                 'res_id':'product.category,'+str(rec.id),
    #                 'company_id':com.id,
    #                 'fields_id':self.env['ir.model.fields'].search([('name','=','property_cost_method'),('model','=','product.category')]).id,
    #                 'value_text':'standard',
    #                 'type':'selection'
    #             }
    #             val_ir_property.append(val)
    #
    #             query = """delete from ir_property where res_id='{}' and name='{}' and company_id={}""".format(
    #                 'product.category,' + str(rec.id), 'property_valuation',com.id)
    #             self._cr.execute(query=query)
    #
    #             val = {
    #                 'name': "property_valuation",
    #                 'res_id': 'product.category,' + str(rec.id),
    #                 'company_id': com.id,
    #                 'fields_id': self.env['ir.model.fields'].search([('name','=','property_valuation'),('model','=','product.category')]).id,
    #                 'value_text': 'real_time',
    #                 'type': 'selection'
    #             }
    #             val_ir_property.append(val)
    #
    #             query = """delete from ir_property where res_id='{}' and name='{}' and company_id={}""".format(
    #                 'product.category,' + str(rec.id), 'property_stock_valuation_account_id',com.id)
    #             self._cr.execute(query=query)
    #
    #             val = {
    #                 'name': "property_stock_valuation_account_id",
    #                 'res_id': 'product.category,' + str(rec.id),
    #                 'company_id': com.id,
    #                 'fields_id': self.env['ir.model.fields'].search([('name','=','property_stock_valuation_account_id'),('model','=','product.category')]).id,
    #                 'value_reference':'account.account,'+str(self.env['account.account'].search([('identity_id', '=', 10),('company_id','=',com.id)]).id),
    #                 'type': 'many2one'
    #             }
    #             val_ir_property.append(val)
    #
    #             query = """delete from ir_property where res_id='{}' and name='{}' and company_id={}""".format(
    #                 'product.category,' + str(rec.id), 'property_stock_account_input_categ_id', com.id)
    #             self._cr.execute(query=query)
    #
    #             val = {
    #                 'name': "property_stock_account_input_categ_id",
    #                 'res_id': 'product.category,' + str(rec.id),
    #                 'company_id': com.id,
    #                 'fields_id': self.env['ir.model.fields'].search([('name','=','property_stock_account_input_categ_id'),('model','=','product.category')]).id,
    #                 'value_reference': 'account.account,' + str(self.env['account.account'].search(
    #                     [('identity_id', '=', 88),('company_id','=',com.id)]).id),
    #                 'type': 'many2one'
    #             }
    #             val_ir_property.append(val)
    #
    #             query = """delete from ir_property where res_id='{}' and name='{}' and company_id={}""".format(
    #                 'product.category,' + str(rec.id), 'property_stock_account_output_categ_id', com.id)
    #             self._cr.execute(query=query)
    #
    #             val = {
    #                 'name': "property_stock_account_output_categ_id",
    #                 'res_id': 'product.category,' + str(rec.id),
    #                 'company_id': com.id,
    #                 'fields_id': self.env['ir.model.fields'].search([('name','=','property_stock_account_output_categ_id'),('model','=','product.category')]).id,
    #                 'value_reference': 'account.account,' + str(self.env['account.account'].search(
    #                     [('identity_id', '=', 89),('company_id','=',com.id)]).id),
    #                 'type': 'many2one'
    #             }
    #             val_ir_property.append(val)
    #
    #             query = """delete from ir_property where res_id='{}' and name='{}' and company_id={}""".format(
    #                 'product.category,' + str(rec.id), 'property_account_income_categ_id', com.id)
    #             self._cr.execute(query=query)
    #
    #             val = {
    #                 'name': "property_account_income_categ_id",
    #                 'res_id': 'product.category,' + str(rec.id),
    #                 'company_id': com.id,
    #                 'fields_id': self.env['ir.model.fields'].search(
    #                     [('name', '=', 'property_account_income_categ_id'),
    #                      ('model', '=', 'product.category')]).id,
    #                 'value_reference': 'account.account,' + str(self.env['account.account'].search(
    #                     [('identity_id', '=', 76), ('company_id', '=', com.id)]).id),
    #                 'type': 'many2one'
    #             }
    #
    #             val_ir_property.append(val)
    #
    #             query = """delete from ir_property where res_id='{}' and name='{}' and company_id={}""".format(
    #                 'product.category,' + str(rec.id), 'property_account_expense_categ_id', com.id)
    #             self._cr.execute(query=query)
    #
    #             val = {
    #                 'name': "property_account_expense_categ_id",
    #                 'res_id': 'product.category,' + str(rec.id),
    #                 'company_id': com.id,
    #                 'fields_id': self.env['ir.model.fields'].search(
    #                     [('name', '=', 'property_account_expense_categ_id'),
    #                      ('model', '=', 'product.category')]).id,
    #                 'value_reference': 'account.account,' + str(self.env['account.account'].search(
    #                     [('identity_id', '=', 79), ('company_id', '=', com.id)]).id),
    #                 'type': 'many2one'
    #             }
    #
    #             query = """delete from ir_property where res_id='{}' and name='{}' and company_id={}""".format(
    #                 'product.category,' + str(rec.id), 'property_stock_journal', com.id)
    #             self._cr.execute(query=query)
    #             val_ir_property.append(val)
    #
    #             val = {
    #                 'name': "property_stock_journal",
    #                 'res_id': 'product.category,' + str(rec.id),
    #                 'company_id': com.id,
    #                 'fields_id': self.env['ir.model.fields'].search(
    #                     [('name', '=', 'property_stock_journal'),
    #                      ('model', '=', 'product.category')]).id,
    #                 'value_reference': 'account.account,' + str(self.env['account.journal'].search(
    #                     [('name', 'like', '%Inventory Valuation%'), ('company_id', '=', com.id)]).id),
    #                 'type': 'many2one'
    #             }
    #             val_ir_property.append(val)
    #
    #         self.env['ir.property'].sudo().create(val_ir_property)
