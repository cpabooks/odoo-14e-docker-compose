# sale_discount# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.
from functools import partial

import odoo.addons.decimal_precision as dp
from odoo import api, fields, models, _
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning
from odoo.tools import float_is_zero, float_compare, formatLang


class sale_order(models.Model):
    _inherit = 'sale.order'

    # def _amount_by_group(self):
    #     for order in self:
    #         line_discount=order_discount=amount_untaxed=0
    #         currency = order.currency_id or order.company_id.currency_id
    #         fmt = partial(formatLang, self.with_context(lang=order.partner_id.lang).env, currency_obj=currency)
    #         res = {}
    #         for line in order.order_line:
    #             amount_untaxed += line.price_subtotal
    #         if order.discount_type == 'line':
    #             for line in order.order_line:
    #                 if line.discount_method == 'fix':
    #                     line_discount = line.discount_amount
    #                 elif line.discount_method == 'per':
    #                     line_discount = line.price_subtotal * (line.discount_amount / 100)
    #                     # price_reduce = line.price_unit * (1.0 - line.discount_amount / 100.0)
    #                 price_reduce= line.price_unit - (line_discount/line.product_uom_qty)
    #                 taxes = line.tax_id.compute_all(price_reduce, quantity=line.product_uom_qty, product=line.product_id, partner=order.partner_shipping_id)['taxes']
    #                 for tax in line.tax_id:
    #                     group = tax.tax_group_id
    #                     res.setdefault(group, {'amount': 0.0, 'base': 0.0})
    #                     for t in taxes:
    #                         if t['id'] == tax.id or t['id'] in tax.children_tax_ids.ids:
    #                             res[group]['amount'] += t['amount']
    #                             res[group]['base'] += t['base']
    #
    #         if order.discount_type == 'global':
    #             # for line in order.order_line:
    #             if order.discount_method == 'fix':
    #                 order_discount = order.discount_amount
    #             elif order.discount_method == 'per':
    #                 order_discount = amount_untaxed * (order.discount_amount / 100)
    #                 # price_reduce = line.price_unit * (1.0 - line.discount_amount / 100.0)
    #             price_reduce= amount_untaxed - order_discount
    #             taxes = line.tax_id.compute_all(price_reduce, quantity=1, product=None, partner=order.partner_shipping_id)['taxes']
    #             for tax in line.tax_id:
    #                 group = tax.tax_group_id
    #                 res.setdefault(group, {'amount': 0.0, 'base': 0.0})
    #                 for t in taxes:
    #                     if t['id'] == tax.id or t['id'] in tax.children_tax_ids.ids:
    #                         res[group]['amount'] += t['amount']
    #                         res[group]['base'] += t['base']
    #         res = sorted(res.items(), key=lambda l: l[0].sequence)
    #         order.amount_by_group = [(
    #             l[0].name, l[1]['amount'], l[1]['base'],
    #             fmt(l[1]['amount']), fmt(l[1]['base']),
    #             len(res),
    #         ) for l in res]

    def _amount_by_group(self):
        for order in self:
            line_discount=order_discount=amount_untaxed=0
            currency = order.currency_id or order.company_id.currency_id
            fmt = partial(formatLang, self.with_context(lang=order.partner_id.lang).env, currency_obj=currency)
            res = {}
            for line in order.order_line:
                amount_untaxed += line.price_subtotal
            if order.discount_type == 'line':
                for line in order.order_line:
                    if line.discount_method == 'fix':
                        line_discount = line.discount_amount
                    elif line.discount_method == 'per':
                        line_discount = line.price_subtotal * (line.discount_amount / 100)
                        # price_reduce = line.price_unit * (1.0 - line.discount_amount / 100.0)
                    price_reduce= line.price_unit - (line_discount/line.product_uom_qty)
                    taxes = line.tax_id.compute_all(price_reduce, quantity=line.product_uom_qty, product=line.product_id, partner=order.partner_shipping_id)['taxes']
                    for tax in line.tax_id:
                        group = tax.tax_group_id
                        res.setdefault(group, {'amount': 0.0, 'base': 0.0})
                        for t in taxes:
                            if t['id'] == tax.id or t['id'] in tax.children_tax_ids.ids:
                                res[group]['amount'] += t['amount']
                                res[group]['base'] += t['base']

            if order.discount_type == 'global':
                # for line in order.order_line:
                if order.discount_method == 'fix':
                    order_discount = order.discount_amount
                elif order.discount_method == 'per':
                    order_discount = amount_untaxed * (order.discount_amount / 100)
                    # price_reduce = line.price_unit * (1.0 - line.discount_amount / 100.0)
                price_reduce= amount_untaxed - order_discount
                taxes=[]
                for line in order.order_line:
                    line_wise_discount=(price_reduce*line.price_subtotal)/amount_untaxed
                    taxes = line.tax_id.compute_all(line_wise_discount, quantity=1, product=None, partner=order.partner_shipping_id)['taxes']
                    for tax in line.tax_id:
                        group = tax.tax_group_id
                        res.setdefault(group, {'amount': 0.0, 'base': 0.0})
                        for t in taxes:
                            if t['id'] == tax.id or t['id'] in tax.children_tax_ids.ids:
                                res[group]['amount'] += t['amount']
                                res[group]['base'] += t['base']
            res = sorted(res.items(), key=lambda l: l[0].sequence)
            order.amount_by_group = [(
                l[0].name, l[1]['amount'], l[1]['base'],
                fmt(l[1]['amount']), fmt(l[1]['base']),
                len(res),
            ) for l in res]

    @api.depends('discount_amount','discount_method','discount_type')
    def _calculate_discount(self):
        res=0.0
        discount = 0.0
        for self_obj in self:
            if self_obj.discount_method == 'fix':
                discount = self_obj.discount_amount
                res = discount
            elif self_obj.discount_method == 'per':
                discount = self_obj.amount_untaxed * (self_obj.discount_amount/ 100)
                res = discount
            else:
                res = discount
        return res


    # @api.depends('order_line','order_line.price_total','order_line.price_subtotal',\
    #     'order_line.product_uom_qty','discount_amount',\
    #     'discount_method','discount_type' ,'order_line.discount_amount',\
    #     'order_line.discount_method','order_line.discount_amt')
    # def _amount_all(self):
    #     """
    #     Compute the total amounts of the SO.
    #     """
    #     res_config= self.env.company
    #     cur_obj = self.env['res.currency']
    #     for order in self:
    #         total_after_discount = applied_discount = line_discount = sums = order_discount =  amount_untaxed = amount_tax = amount_after_discount =  0.0
    #         for line in order.order_line:
    #             amount_untaxed += line.price_subtotal
    #             amount_tax += line.price_tax
    #             applied_discount += line.discount_amt
    #
    #             if line.discount_method == 'fix':
    #                 line_discount += line.discount_amount
    #             elif line.discount_method == 'per':
    #                 line_discount += line.price_subtotal * (line.discount_amount/ 100)
    #
    #         if res_config.tax_discount_policy:
    #             if res_config.tax_discount_policy == 'tax':
    #                 if order.discount_type == 'line':
    #                     order.discount_amt = 0.00
    #                     order.update({
    #                         'amount_untaxed': amount_untaxed,
    #                         'amount_tax': amount_tax,
    #                         'amount_total': amount_untaxed + amount_tax - line_discount,
    #                         'discount_amt_line' : line_discount,
    #                         'total_after_discount': amount_untaxed - line_discount,
    #                     })
    #
    #                 elif order.discount_type == 'global':
    #                     order.discount_amt_line = 0.00
    #
    #                     if order.discount_method == 'per':
    #                         order_discount = amount_untaxed * (order.discount_amount / 100)
    #                         order.update({
    #                             'amount_untaxed': amount_untaxed,
    #                             'amount_tax': amount_tax,
    #                             'amount_total': amount_untaxed + amount_tax - order_discount,
    #                             'discount_amt' : order_discount,
    #                             'total_after_discount': amount_untaxed - order_discount,
    #                         })
    #                     elif order.discount_method == 'fix':
    #                         order_discount = order.discount_amount
    #                         order.update({
    #                             'amount_untaxed': amount_untaxed,
    #                             'amount_tax': amount_tax,
    #                             'amount_total': amount_untaxed + amount_tax - order_discount,
    #                             'discount_amt' : order_discount,
    #                             'total_after_discount': amount_untaxed - order_discount,
    #                         })
    #                     else:
    #                         order.update({
    #                             'amount_untaxed': amount_untaxed,
    #                             'amount_tax': amount_tax,
    #                             'amount_total': amount_untaxed + amount_tax ,
    #                         })
    #                 else:
    #                     order.update({
    #                         'amount_untaxed': amount_untaxed,
    #                         'amount_tax': amount_tax,
    #                         'amount_total': amount_untaxed + amount_tax ,
    #                         })
    #             elif res_config.tax_discount_policy == 'untax':
    #                 if order.discount_type == 'line':
    #                     order.discount_amt = 0.00
    #                     order.update({
    #                         'amount_untaxed': amount_untaxed,
    #                         'amount_tax': amount_tax,
    #                         'amount_total': amount_untaxed + amount_tax - applied_discount,
    #                         'discount_amt_line' : applied_discount,
    #                         'total_after_discount': amount_untaxed - applied_discount,
    #                     })
    #                 elif order.discount_type == 'global':
    #                     order.discount_amt_line = 0.00
    #                     if order.discount_method == 'fix':
    #                         order_discount = order.discount_amount
    #                         price_reduce = amount_untaxed - order_discount
    #                         taxes = line.tax_id.compute_all(round(price_reduce, 2), \
    #                                                         order.currency_id, 1.0, product=line.product_id, \
    #                                                         partner=order.partner_id)
    #                         sums += sum(t.get('amount', 0.0) for t in taxes.get('taxes', []))
    #                         order.update({
    #                             'amount_untaxed': amount_untaxed,
    #                             'amount_tax': sums,
    #                             'amount_total': amount_untaxed + sums - order_discount,
    #                             'discount_amt': order_discount,
    #                             'total_after_discount': amount_untaxed - order_discount,
    #                         })
    #                     elif order.discount_method == 'per':
    #                         order_discount = amount_untaxed * (order.discount_amount / 100)
    #                         price_reduce = amount_untaxed - order_discount
    #                         # price_reduce = line.price_unit * (1.0 - line.discount_amount / 100.0)
    #                         taxes = line.tax_id.compute_all(price_reduce, \
    #                                                         order.currency_id, 1.0, product=line.product_id, \
    #                                                         partner=order.partner_id)
    #                         sums += sum(t.get('amount', 0.0) for t in taxes.get('taxes', []))
    #                         order.update({
    #                             'amount_untaxed': amount_untaxed,
    #                             'amount_tax': sums,
    #                             'amount_total': amount_untaxed + sums - order_discount,
    #                             'discount_amt': order_discount,
    #                             'total_after_discount': amount_untaxed - order_discount,
    #                         })
    #
    #                     else:
    #                         order.update({
    #                             'amount_untaxed': amount_untaxed,
    #                             'amount_tax': amount_tax,
    #                             'amount_total': amount_untaxed + amount_tax ,
    #                         })
    #
    #                     # if order.discount_method == 'per':
    #                     #     order_discount = amount_untaxed * (order.discount_amount / 100)
    #                     #     if order.order_line:
    #                     #         for line in order.order_line:
    #                     #             if line.tax_id:
    #                     #                 final_discount = 0.0
    #                     #                 try:
    #                     #                     final_discount = ((order.discount_amount*line.price_subtotal)/100.0)
    #                     #                 except ZeroDivisionError:
    #                     #                     pass
    #                     #                 discount = line.price_subtotal - final_discount
    #                     #                 taxes = line.tax_id.compute_all(discount, \
    #                     #                                     order.currency_id,1.0, product=line.product_id, \
    #                     #                                     partner=order.partner_id)
    #                     #                 sums += sum(t.get('amount', 0.0) for t in taxes.get('taxes', []))
    #                     #     order.update({
    #                     #         'amount_untaxed': amount_untaxed,
    #                     #         'amount_tax': sums,
    #                     #         'amount_total': amount_untaxed + sums - order_discount,
    #                     #         'discount_amt' : order_discount,
    #                     #         'total_after_discount': amount_untaxed - order_discount,
    #                     #     })
    #                     # elif order.discount_method == 'fix':
    #                     #     order_discount = order.discount_amount
    #                     #     if order.order_line:
    #                     #         for line in order.order_line:
    #                     #             if line.tax_id:
    #                     #                 final_discount = 0.0
    #                     #                 try:
    #                     #                     final_discount = ((order.discount_amount*line.price_subtotal)/amount_untaxed)
    #                     #                 except ZeroDivisionError:
    #                     #                     pass
    #                     #                 discount = line.price_subtotal - final_discount
    #                     #
    #                     #                 taxes = line.tax_id.compute_all(round(discount,2), \
    #                     #                                     order.currency_id,1.0, product=line.product_id, \
    #                     #                                     partner=order.partner_id)
    #                     #                 sums += sum(t.get('amount', 0.0) for t in taxes.get('taxes', []))
    #                     #     order.update({
    #                     #         'amount_untaxed': amount_untaxed,
    #                     #         'amount_tax': sums,
    #                     #         'amount_total': amount_untaxed + sums - order_discount,
    #                     #         'discount_amt' : order_discount,
    #                     #         'total_after_discount': amount_untaxed - order_discount,
    #                     #     })
    #                     # else:
    #                     #     order.update({
    #                     #         'amount_untaxed': amount_untaxed,
    #                     #         'amount_tax': amount_tax,
    #                     #         'amount_total': amount_untaxed + amount_tax ,
    #                     #     })
    #                 else:
    #                     order.update({
    #                         'amount_untaxed': amount_untaxed,
    #                         'amount_tax': amount_tax,
    #                         'amount_total': amount_untaxed + amount_tax ,
    #                         })
    #             else:
    #                 order.update({
    #                         'amount_untaxed': amount_untaxed,
    #                         'amount_tax': amount_tax,
    #                         'amount_total': amount_untaxed + amount_tax ,
    #                         })
    #         else:
    #             order.update({
    #                 'amount_untaxed': amount_untaxed,
    #                 'amount_tax': amount_tax,
    #                 'amount_total': amount_untaxed + amount_tax ,
    #                 })
    @api.depends('order_line', 'order_line.price_total', 'order_line.price_subtotal', \
                 'order_line.product_uom_qty', 'discount_amount', \
                 'discount_method', 'discount_type', 'order_line.discount_amount', \
                 'order_line.discount_method', 'order_line.discount_amt')
    def _amount_all(self):
        """
        Compute the total amounts of the SO.
        """
        res_config = self.env.company
        cur_obj = self.env['res.currency']
        for order in self:
            total_after_discount = applied_discount = line_discount = sums = order_discount = amount_untaxed = amount_tax = amount_after_discount = 0.0
            for line in order.order_line:
                amount_untaxed += line.price_subtotal
                amount_tax += line.price_tax
                applied_discount += line.discount_amt

                if line.discount_method == 'fix':
                    line_discount += line.discount_amount
                elif line.discount_method == 'per':
                    line_discount += line.price_subtotal * (line.discount_amount / 100)

            if res_config.tax_discount_policy:
                if res_config.tax_discount_policy == 'tax':
                    if order.discount_type == 'line':
                        order.discount_amt = 0.00
                        order.update({
                            'amount_untaxed': amount_untaxed,
                            'amount_tax': amount_tax,
                            'amount_total': amount_untaxed + amount_tax - line_discount,
                            'discount_amt_line': line_discount,
                            'total_after_discount': amount_untaxed - line_discount,
                        })

                    elif order.discount_type == 'global':
                        order.discount_amt_line = 0.00

                        if order.discount_method == 'per':
                            order_discount = amount_untaxed * (order.discount_amount / 100)
                            order.update({
                                'amount_untaxed': amount_untaxed,
                                'amount_tax': amount_tax,
                                'amount_total': amount_untaxed + amount_tax - order_discount,
                                'discount_amt': order_discount,
                                'total_after_discount': amount_untaxed - order_discount,
                            })
                        elif order.discount_method == 'fix':
                            order_discount = order.discount_amount
                            order.update({
                                'amount_untaxed': amount_untaxed,
                                'amount_tax': amount_tax,
                                'amount_total': amount_untaxed + amount_tax - order_discount,
                                'discount_amt': order_discount,
                                'total_after_discount': amount_untaxed - order_discount,
                            })
                        else:
                            order.update({
                                'amount_untaxed': amount_untaxed,
                                'amount_tax': amount_tax,
                                'amount_total': amount_untaxed + amount_tax,
                            })
                    else:
                        order.update({
                            'amount_untaxed': amount_untaxed,
                            'amount_tax': amount_tax,
                            'amount_total': amount_untaxed + amount_tax,
                        })
                elif res_config.tax_discount_policy == 'untax':
                    if order.discount_type == 'line':
                        order.discount_amt = 0.00
                        order.update({
                            'amount_untaxed': amount_untaxed,
                            'amount_tax': amount_tax,
                            'amount_total': amount_untaxed + amount_tax - applied_discount,
                            'discount_amt_line': applied_discount,
                            'total_after_discount': amount_untaxed - applied_discount,
                        })
                    elif order.discount_type == 'global':
                        order.discount_amt_line = 0.00
                        if order.discount_method == 'fix':
                            order_discount = order.discount_amount
                            price_reduce = amount_untaxed - order_discount
                            for line in order.order_line:
                                line_wise_discount = (price_reduce * line.price_subtotal) / amount_untaxed
                                taxes = line.tax_id.compute_all(round(line_wise_discount, 2), \
                                                                order.currency_id, 1.0, product=line.product_id, \
                                                                partner=order.partner_id)
                                sums += sum(t.get('amount', 0.0) for t in taxes.get('taxes', []))
                            order.update({
                                'amount_untaxed': amount_untaxed,
                                'amount_tax': sums,
                                'amount_total': amount_untaxed + sums - order_discount,
                                'discount_amt': order_discount,
                                'total_after_discount': amount_untaxed - order_discount,
                            })
                        elif order.discount_method == 'per':
                            order_discount = amount_untaxed * (order.discount_amount / 100)
                            price_reduce = amount_untaxed - order_discount
                            # price_reduce = line.price_unit * (1.0 - line.discount_amount / 100.0)
                            # taxes = line.tax_id.compute_all(price_reduce, \
                            #                                 order.currency_id, 1.0, product=line.product_id, \
                            #                                 partner=order.partner_id)
                            # sums += sum(t.get('amount', 0.0) for t in taxes.get('taxes', []))
                            for line in order.order_line:
                                line_wise_discount = (price_reduce * line.price_subtotal) / amount_untaxed
                                taxes = line.tax_id.compute_all(round(line_wise_discount, 2), \
                                                                order.currency_id, 1.0, product=line.product_id, \
                                                                partner=order.partner_id)
                                sums += sum(t.get('amount', 0.0) for t in taxes.get('taxes', []))
                            order.update({
                                'amount_untaxed': amount_untaxed,
                                'amount_tax': sums,
                                'amount_total': amount_untaxed + sums - order_discount,
                                'discount_amt': order_discount,
                                'total_after_discount': amount_untaxed - order_discount,
                            })

                        else:
                            order.update({
                                'amount_untaxed': amount_untaxed,
                                'amount_tax': amount_tax,
                                'amount_total': amount_untaxed + amount_tax,
                            })

                        # if order.discount_method == 'per':
                        #     order_discount = amount_untaxed * (order.discount_amount / 100)
                        #     if order.order_line:
                        #         for line in order.order_line:
                        #             if line.tax_id:
                        #                 final_discount = 0.0
                        #                 try:
                        #                     final_discount = ((order.discount_amount*line.price_subtotal)/100.0)
                        #                 except ZeroDivisionError:
                        #                     pass
                        #                 discount = line.price_subtotal - final_discount
                        #                 taxes = line.tax_id.compute_all(discount, \
                        #                                     order.currency_id,1.0, product=line.product_id, \
                        #                                     partner=order.partner_id)
                        #                 sums += sum(t.get('amount', 0.0) for t in taxes.get('taxes', []))
                        #     order.update({
                        #         'amount_untaxed': amount_untaxed,
                        #         'amount_tax': sums,
                        #         'amount_total': amount_untaxed + sums - order_discount,
                        #         'discount_amt' : order_discount,
                        #         'total_after_discount': amount_untaxed - order_discount,
                        #     })
                        # elif order.discount_method == 'fix':
                        #     order_discount = order.discount_amount
                        #     if order.order_line:
                        #         for line in order.order_line:
                        #             if line.tax_id:
                        #                 final_discount = 0.0
                        #                 try:
                        #                     final_discount = ((order.discount_amount*line.price_subtotal)/amount_untaxed)
                        #                 except ZeroDivisionError:
                        #                     pass
                        #                 discount = line.price_subtotal - final_discount
                        #
                        #                 taxes = line.tax_id.compute_all(round(discount,2), \
                        #                                     order.currency_id,1.0, product=line.product_id, \
                        #                                     partner=order.partner_id)
                        #                 sums += sum(t.get('amount', 0.0) for t in taxes.get('taxes', []))
                        #     order.update({
                        #         'amount_untaxed': amount_untaxed,
                        #         'amount_tax': sums,
                        #         'amount_total': amount_untaxed + sums - order_discount,
                        #         'discount_amt' : order_discount,
                        #         'total_after_discount': amount_untaxed - order_discount,
                        #     })
                        # else:
                        #     order.update({
                        #         'amount_untaxed': amount_untaxed,
                        #         'amount_tax': amount_tax,
                        #         'amount_total': amount_untaxed + amount_tax ,
                        #     })
                    else:
                        order.update({
                            'amount_untaxed': amount_untaxed,
                            'amount_tax': amount_tax,
                            'amount_total': amount_untaxed + amount_tax,
                        })
                else:
                    order.update({
                        'amount_untaxed': amount_untaxed,
                        'amount_tax': amount_tax,
                        'amount_total': amount_untaxed + amount_tax,
                    })
            else:
                order.update({
                    'amount_untaxed': amount_untaxed,
                    'amount_tax': amount_tax,
                    'amount_total': amount_untaxed + amount_tax,
                })

    discount_method = fields.Selection([('fix', 'Fixed'), ('per', 'Percentage')], 'Discount Method')
    discount_amount = fields.Float('Discount Amount')
    discount_amt = fields.Monetary(compute='_amount_all', string='- Discount', store=True, readonly=True)
    discount_type = fields.Selection([('line', 'Order Line'), ('global', 'Global')],string='Discount Applies to',default='global')
    discount_amt_line = fields.Float(compute='_amount_all', string='- Line Discount', digits=(16, 4), store=True, readonly=True)
    total_after_discount = fields.Float(compute='_amount_all', string='Total After Discount', digits=(16, 4), store=True, readonly=True)

    def _prepare_invoice(self):
        res = super(sale_order,self)._prepare_invoice()
        res.update({'discount_method': self.discount_method,
                'discount_amount': self.discount_amount,
                'discount_amt': self.discount_amt,
                'discount_type': self.discount_type,
                'discount_amt_line' : self.discount_amt_line,
                'total_after_discount': self.total_after_discount
                })
        return res



class sale_order_line(models.Model):
    _inherit = 'sale.order.line'

    @api.depends('product_uom_qty', 'discount', 'price_unit', 'tax_id','discount_method','discount_amount')
    def _compute_amount(self):
        """
        Compute the amounts of the SO line.
        """
        res_config= self.env.company
        for line in self:
            if res_config.tax_discount_policy:
                if res_config.tax_discount_policy == 'untax':
                    if line.discount_type == 'line':
                        if line.discount_method == 'fix':
                            price = (line.price_unit * line.product_uom_qty) - line.discount_amount
                            taxes = line.tax_id.compute_all(price, line.order_id.currency_id, 1, product=line.product_id, partner=line.order_id.partner_shipping_id)
                            line.update({
                                'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
                                'price_total': taxes['total_included'] + line.discount_amount,
                                'price_subtotal': taxes['total_excluded'] + line.discount_amount,
                                'discount_amt' : line.discount_amount,
                            })

                        elif line.discount_method == 'per':
                            price = (line.price_unit * line.product_uom_qty) * (1 - (line.discount_amount or 0.0) / 100.0)
                            price_x = ((line.price_unit * line.product_uom_qty) - (line.price_unit * line.product_uom_qty) * (1 - (line.discount_amount or 0.0) / 100.0))
                            taxes = line.tax_id.compute_all(price, line.order_id.currency_id, 1, product=line.product_id, partner=line.order_id.partner_shipping_id)
                            line.update({
                                'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
                                'price_total': taxes['total_included'] + price_x,
                                'price_subtotal': taxes['total_excluded'] + price_x,
                                'discount_amt' : price_x,
                            })
                        else:
                            price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
                            taxes = line.tax_id.compute_all(price, line.order_id.currency_id, line.product_uom_qty, product=line.product_id, partner=line.order_id.partner_shipping_id)
                            line.update({
                                'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
                                'price_total': taxes['total_included'],
                                'price_subtotal': taxes['total_excluded'],
                            })
                    else:
                        price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
                        taxes = line.tax_id.compute_all(price, line.order_id.currency_id, line.product_uom_qty, product=line.product_id, partner=line.order_id.partner_shipping_id)
                        line.update({
                            'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
                            'price_total': taxes['total_included'],
                            'price_subtotal': taxes['total_excluded'],
                        })
                elif res_config.tax_discount_policy == 'tax':
                    if line.discount_type == 'line':
                        price_x = 0.0
                        price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
                        taxes = line.tax_id.compute_all(price, line.order_id.currency_id, line.product_uom_qty, product=line.product_id, partner=line.order_id.partner_shipping_id)

                        if line.discount_method == 'fix':
                            price_x = (taxes['total_included']) - ( taxes['total_included'] - line.discount_amount)
                        elif line.discount_method == 'per':
                            price_x = (taxes['total_included']) - (taxes['total_included'] * (1 - (line.discount_amount or 0.0) / 100.0))
                        else:
                            price_x = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
                
                        line.update({
                            'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
                            'price_total': taxes['total_included'],
                            'price_subtotal': taxes['total_excluded'],
                            'discount_amt' : price_x,
                        })
                    else:
                        price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
                        taxes = line.tax_id.compute_all(price, line.order_id.currency_id, line.product_uom_qty, product=line.product_id, partner=line.order_id.partner_shipping_id)
                        line.update({
                            'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
                            'price_total': taxes['total_included'],
                            'price_subtotal': taxes['total_excluded'],
                        })
                else:
                    price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
                    taxes = line.tax_id.compute_all(price, line.order_id.currency_id, line.product_uom_qty, product=line.product_id, partner=line.order_id.partner_shipping_id)
                    
                    line.update({
                        'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
                        'price_total': taxes['total_included'],
                        'price_subtotal': taxes['total_excluded'],
                    })
            else:
                price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
                taxes = line.tax_id.compute_all(price, line.order_id.currency_id, line.product_uom_qty, product=line.product_id, partner=line.order_id.partner_shipping_id)
                
                line.update({
                    'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
                    'price_total': taxes['total_included'],
                    'price_subtotal': taxes['total_excluded'],
                })

    is_apply_on_discount_amount =  fields.Boolean("Tax Apply After Discount")
    discount_method = fields.Selection([('fix', 'Fixed'), ('per', 'Percentage')], 'Discount Method')
    discount_type = fields.Selection(related='order_id.discount_type', string="Discount Applies to")
    discount_amount = fields.Float('Discount Amount')
    discount_amt = fields.Float('Discount Final Amount')

    def _prepare_invoice_line(self,**optional_values):
        res = super(sale_order_line,self)._prepare_invoice_line(**optional_values)
        res.update({'discount': self.discount,
                    'discount_method':self.discount_method,
                    'discount_amount':self.discount_amount,
                    'discount_amt' : self.discount_amt,})
        return res


class ResCompany(models.Model):
    _inherit = 'res.company'

    tax_discount_policy = fields.Selection([('tax', 'Tax Amount'), ('untax', 'Untax Amount')],
        default_model='sale.order',default='tax')


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    tax_discount_policy = fields.Selection([('tax', 'Tax Amount'), ('untax', 'Untax Amount')],readonly=False,related='company_id.tax_discount_policy',string='Discount Applies On',default_model='sale.order'
        )
