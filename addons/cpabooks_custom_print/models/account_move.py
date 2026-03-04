# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class AccountMove(models.Model):
    _inherit = 'account.move'

    delivery_detail = fields.Char(string='Delivery')
    make_detail = fields.Char(string='Make')
    num_word = fields.Char(string='Amount in Words: ', compute='_compute_amount_in_word')

    @api.depends('amount_total')
    def _compute_amount_in_word(self):
        for invoice in self:
            invoice.num_word = ''
            if invoice.currency_id:
                invoice.num_word = str(invoice.currency_id.amount_to_text(invoice.amount_total))

    def in_word(self,total_amount):
        for invoice in self:
            if invoice.currency_id:
                return str(invoice.currency_id.amount_to_text(total_amount))

    def get_signature(self):
        get_signature_data=self.env['signature.setup'].search([('model','=','account.move'),('company_id','=',self.env.company.id)])
        return get_signature_data

    def get_table_data(self):
        for rec in self:
            if rec.move_type=='out_invoice':
                query="""select product_name,uom_name,sum(quantity) as total,sum(previous_qty) as previous,sum(present_qty) as present,sum(still_now) as still_now, unit_price from (
                        (select am.id as invoice_id,aml.id as invoice_line_id ,pt.name as product_name,um.name as uom_name,aml.quantity as quantity,0 as previous_qty,aml.quantity as present_qty,aml.quantity as still_now,aml.price_unit as unit_price from account_move am
                        left join account_move_line aml on aml.move_id=am.id 
                        left join product_product pp on pp.id=aml.product_id
                        left join product_template pt on pt.id=pp.product_tmpl_id
                        left join uom_uom um on um.id=aml.product_uom_id
                        where am.invoice_origin='{}' and  am.id={} and am.company_id={} and am.state='posted' and aml.product_id is not null  and tax_line_id is null  order by am.id desc limit 1)
                        UNION all
                        (select am.id as invoice_id,aml.id as invoice_line_id,pt.name as product_name,um.name as uom_name,aml.quantity as quantity,sum(aml.quantity) as previous_qty,0 as present_qty,sum(aml.quantity)as still_now,aml.price_unit as unit_price from account_move am
                        left join account_move_line aml on aml.move_id=am.id 
                        left join product_product pp on pp.id=aml.product_id
                        left join product_template pt on pt.id=pp.product_tmpl_id
                        left join uom_uom um on um.id=aml.product_uom_id
                        where aml.id not in(
                        
                            select aml.id  from account_move am
                            left join account_move_line aml on aml.move_id=am.id 
                            left join product_product pp on pp.id=aml.product_id
                            left join product_template pt on pt.id=pp.product_tmpl_id
                            left join uom_uom um on um.id=aml.product_uom_id
                            where am.invoice_origin='{}' and am.id={} and am.company_id={} and am.state='posted' and  aml.product_id is not null and tax_line_id is null  order by am.id desc limit 1
                        
                        )and  am.invoice_origin='{}' and am.id<={} and am.company_id={} and am.state='posted' and aml.product_id is not null and tax_line_id is null group by am.id,aml.id,pt.name,um.name,aml.quantity,aml.price_unit 
                        order by am.id desc) ) as test group by product_name,uom_name,unit_price""".format(rec.invoice_origin,rec.id,rec.company_id.id,rec.invoice_origin,rec.id,rec.company_id.id,rec.invoice_origin,rec.id,rec.company_id.id)
                self._cr.execute(query=query)
                query_result=self._cr.fetchall()
                get_so=self.env['sale.order'].sudo().search([('name','=',rec.invoice_origin)])

                collection_data=dict()

                for so_line in get_so.order_line:
                    for inv_line in query_result:
                        if so_line.product_id.name==inv_line[0]:
                            product=so_line.product_id.name
                            if product not in collection_data.keys():
                                collection_data[product]=list()
                                query_result_list=list(inv_line)
                                query_result_list[2]=so_line.product_uom_qty
                                inv_line=tuple(query_result_list)
                                collection_data[product].append(inv_line)
        return collection_data

    def _move_autocomplete_invoice_lines_values(self):
        ''' This method recomputes dynamic lines on the current journal entry that include taxes, cash rounding
        and payment terms lines.
        '''
        self.ensure_one()

        for line in self.line_ids:
            # Do something only on invoice lines.
            if line.exclude_from_invoice_tab:
                continue

            # Shortcut to load the demo data.
            # Doing line.account_id triggers a default_get(['account_id']) that could returns a result.
            # A section / note must not have an account_id set.
            if not line._cache.get('account_id') and not line.display_type and not line._origin:
                line.account_id = line._get_computed_account() or self.journal_id.default_account_id
            if line.product_id and not line._cache.get('name') and (line.name == '' or line.name=='/'):
                line.name = line._get_computed_name()

            # Compute the account before the partner_id
            # In case account_followup is installed
            # Setting the partner will get the account_id in cache
            # If the account_id is not in cache, it will trigger the default value
            # Which is wrong in some case
            # It's better to set the account_id before the partner_id
            # Ensure related fields are well copied.
            line.partner_id = self.partner_id
            line.date = self.date
            line.recompute_tax_line = True
            line.currency_id = self.currency_id

        self.line_ids._onchange_price_subtotal()
        self._recompute_dynamic_lines(recompute_all_taxes=True)

        values = self._convert_to_write(self._cache)
        values.pop('invoice_line_ids', None)
        return values

    # def _get_computed_name(self):
    #     self.ensure_one()
    #
    #     if not self.product_id:
    #         return ''
    #
    #     if self.partner_id.lang:
    #         product = self.product_id.with_context(lang=self.partner_id.lang)
    #     else:
    #         product = self.product_id
    #
    #     values = []
    #     if product.partner_ref:
    #         values.append(product.partner_ref)
    #     if self.journal_id.type == 'sale':
    #         if product.description_sale and self.name == '':
    #             values.append(product.description_sale)
    #     elif self.journal_id.type == 'purchase':
    #         if product.description_purchase:
    #             values.append(product.description_purchase)
    #     return '\n'.join(values)












