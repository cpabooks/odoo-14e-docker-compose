from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError


class JobEstimateInherit(models.Model):
    _inherit = "job.estimate"

    final_product_ids=fields.One2many('estimation.final.product','job_estimate_id',copy=True)
    raw_materials=fields.One2many('raw.material.summary','job_estimate_id',copy=True)

    final_material_estimate = fields.Float(compute='_compute_final_job_estimate', string='Final Material Estimate',
                                           readonly=True)
    final_labour_estimate = fields.Float(compute='_compute_final_job_estimate', string='Final Labour Estimate',
                                           readonly=True)
    final_overhead_estimate = fields.Float(compute='_compute_final_job_estimate', string='Final Overhead Estimate',
                                           readonly=True)

    final_total_job_estimation=fields.Float(compute='_compute_final_job_estimate', string='Final Total Job Estimate',
                                           readonly=True)

    final_profit_amount=fields.Float(compute='_compute_final_job_estimate', string='Final Profit Amount',
                                           readonly=True)

    @api.depends('labour_estimation_ids.subtotal', 'overhead_estimation_ids.subtotal',
                 'material_estimation_ids.subtotal', 'final_product_ids.final_amount', 'profit_percent','material_estimation_ids','labour_estimation_ids','overhead_estimation_ids')
    def _compute_final_job_estimate(self):
        for order in self:
            order.final_material_estimate=0
            fianl_total_amount=0
            order.total_labour_estimate=0
            order.total_overhead_estimate=0
            order.total_material_estimate=0
            for line in order.labour_estimation_ids:
                labour_price = (line.quantity * line.price_unit * line.hours) - (
                        line.quantity * line.price_unit * line.hours) * (line.discount or 0.0) / 100.0
                order.total_labour_estimate += labour_price
                # fianl_total_amount+=labour_price*line.final_quantity

            for line in order.overhead_estimation_ids:
                overhead_price = (line.quantity * line.price_unit) - (line.quantity * line.price_unit) * (
                        line.discount or 0.0) / 100.0
                order.total_overhead_estimate += overhead_price
                # fianl_total_amount +=overhead_price*line.final_quantity

            for line in order.material_estimation_ids:
                material_price = (line.quantity * line.price_unit) - (line.quantity * line.price_unit) * (
                        line.discount or 0.0) / 100.0
                order.total_material_estimate += material_price
                # fianl_total_amount += material_price

            total_material_price=0
            total_labour_price=0
            total_overhead_price=0
            final_profit_amount=0
            for fpo_line in order.final_product_ids:
                total_material_price += fpo_line.material_cost * fpo_line.final_quantity
                total_labour_price+=fpo_line.labour_cost * fpo_line.final_quantity
                total_overhead_price += fpo_line.overhead_cost * fpo_line.final_quantity
                final_profit_amount+=fpo_line.profit_amount * fpo_line.final_quantity



            order.final_material_estimate = total_material_price
            order.final_labour_estimate = total_labour_price
            order.final_overhead_estimate = total_overhead_price
            order.final_profit_amount = final_profit_amount
            order.final_total_job_estimation = total_material_price + total_labour_price + total_overhead_price+final_profit_amount

            total = order.total_labour_estimate + order.total_overhead_estimate + order.total_material_estimate
            if order.profit_percent != 0:
                order.total_job_estimate = total + (total * order.profit_percent / 100)

            else:
                order.total_job_estimate = total


    @api.onchange('profit_percent')
    def set_profit_amount(self):
        for rec in self:
            if rec.profit_percent>=0:
                get_total_profit=(rec.total_material_estimate+rec.total_labour_estimate+rec.total_overhead_estimate)*(rec.profit_percent/100)
                if (rec.total_material_estimate+rec.total_labour_estimate+rec.total_overhead_estimate)>0:
                    get_single_profit=get_total_profit/(rec.total_material_estimate+rec.total_labour_estimate+rec.total_overhead_estimate)
                else:
                    get_single_profit=0
                for fp_line in rec.final_product_ids:
                    fp_line.profit_amount=(fp_line.material_cost+fp_line.labour_cost+fp_line.overhead_cost)*get_single_profit
                    fp_line.amount=fp_line.material_cost+fp_line.labour_cost+fp_line.overhead_cost+fp_line.profit_amount
                    fp_line.final_amount = fp_line.final_quantity * fp_line.amount

    @api.onchange('material_estimation_ids')
    def set_final_products(self):
        for rec in self:
            for fp in rec.final_product_ids:
                flag = 0
                if fp.final_product_id.id in rec.material_estimation_ids.bom_product_id.ids:
                    flag=1
                if flag==0:
                    rec.final_product_ids-=fp

            #raw material
            for fp in rec.raw_materials:
                flag = 0
                if fp.product_id.id in rec.material_estimation_ids.product_id.ids:
                    flag=1
                if flag==0:
                    rec.raw_materials-=fp

            # labour cost
            for fp in rec.labour_estimation_ids:
                flag = 0
                if fp.product_id.id in rec.material_estimation_ids.bom_product_id.ids:
                    flag=1
                if flag==0:
                    rec.labour_estimation_ids-=fp


            # overhead cost
            for fp in rec.overhead_estimation_ids:
                flag = 0
                if fp.product_id.id in rec.material_estimation_ids.bom_product_id.ids:
                    flag=1
                if flag == 0:
                    rec.overhead_estimation_ids -= fp

            get_total_profit = (
                                           rec.total_material_estimate + rec.total_labour_estimate + rec.total_overhead_estimate) * (
                                       rec.profit_percent / 100)
            if (rec.total_material_estimate + rec.total_labour_estimate + rec.total_overhead_estimate) > 0:
                get_single_profit = get_total_profit / (
                        rec.total_material_estimate + rec.total_labour_estimate + rec.total_overhead_estimate)
            else:
                get_single_profit=0

            for mt_line in rec.material_estimation_ids:
                if mt_line.bom_product_id and mt_line.bom_product_id.id  not in rec.final_product_ids.final_product_id.ids:
                    val = [(0,0,{
                        'final_product_id': mt_line.bom_product_id.id,
                        # 'quantity':line.task_id.id,
                        'material_cost': mt_line.subtotal,
                        'amount':mt_line.subtotal,
                        'profit_amount':mt_line.subtotal*(rec.profit_percent/100),
                        'final_quantity':1,
                        'final_amount':mt_line.subtotal*(rec.profit_percent/100)+mt_line.subtotal

                    })]
                    rec.final_product_ids=val
                else:
                    get_fp=rec.final_product_ids.filtered(lambda x:x.final_product_id.id==mt_line.bom_product_id.id)
                    get_total_of_ml=sum(rec.material_estimation_ids.filtered(lambda x:x.bom_product_id.id==get_fp.final_product_id.id).mapped("subtotal"))
                    get_fp.material_cost=get_total_of_ml
                    get_fp.profit_amount = (get_fp.material_cost + get_fp.labour_cost + get_fp.overhead_cost) * get_single_profit
                    get_fp.amount=get_fp.material_cost+get_fp.labour_cost+get_fp.overhead_cost+get_fp.profit_amount
                    get_fp.final_amount=get_fp.amount*get_fp.final_quantity

            #raw material
            for mt_line in rec.material_estimation_ids:
                if mt_line.product_id and mt_line.product_id.id not in rec.raw_materials.product_id.ids:
                    val = [(0, 0, {
                        'product_id': mt_line.product_id.id,
                        'quantity':mt_line.quantity,

                    })]
                    rec.raw_materials = val
                else:
                    get_rm = rec.raw_materials.filtered(
                        lambda x: x.product_id.id == mt_line.product_id.id)
                    get_ml_qty=sum(rec.material_estimation_ids.filtered(lambda x:x.product_id.id==get_rm.product_id.id).mapped('quantity'))
                    get_rm.quantity = get_ml_qty



                    # rec.final_product_ids=[(5,0,0)]
                    # product_dict={}
                    # for mt_line in rec.material_estimation_ids:
                    #     if mt_line.bom_product_id.id not in product_dict.keys():
                    #         product_dict[mt_line.bom_product_id.id]=mt_line.subtotal
                    #     else:
                    #         product_dict[mt_line.bom_product_id.id] += mt_line.subtotal
                    #
                    # for p_dict in product_dict.keys():
                    #     val = [(0, 0, {
                    #         'final_product_id': p_dict,
                    #         # 'quantity':line.task_id.id,
                    #         'material_cost': product_dict[p_dict],
                    #         'amount': product_dict[p_dict]
                    #     })]
                    #     rec.final_product_ids = val

            #labour cost
            for mt_line in rec.material_estimation_ids:
                if mt_line.bom_product_id and mt_line.bom_product_id.id  not in rec.labour_estimation_ids.product_id.ids:
                    val = [(0,0,{
                        'product_id': mt_line.bom_product_id.id,
                        'uom_id' : mt_line.bom_product_id.uom_id.id,
                        'price_unit' : mt_line.bom_product_id.list_price
                    })]
                    rec.labour_estimation_ids=val
                else:
                    get_lc = rec.labour_estimation_ids.filtered(
                        lambda x: x.product_id.id == mt_line.bom_product_id.id)
                    get_fp = rec.final_product_ids.filtered(
                        lambda x: x.final_product_id.id == mt_line.bom_product_id.id)
                    get_fp.labour_cost=get_lc.subtotal
                    get_fp.profit_amount = (get_fp.material_cost + get_fp.labour_cost + get_fp.overhead_cost) * get_single_profit
                    get_fp.amount = get_fp.material_cost + get_fp.labour_cost + get_fp.overhead_cost+get_fp.profit_amount
                    get_fp.final_amount=get_fp.amount*get_fp.final_quantity


                    # rec.labour_estimation_ids=[(5,0,0)]
                    # product_dict={}
                    # for mt_line in rec.material_estimation_ids:
                    #     if mt_line.bom_product_id.id not in product_dict.keys():
                    #         product_dict[mt_line.bom_product_id.id]=mt_line.subtotal
                    #     else:
                    #         product_dict[mt_line.bom_product_id.id] += mt_line.subtotal
                    #
                    # for p_dict in product_dict.keys():
                    #     get_product=self.env['product.product'].search([('id','=',p_dict)])
                    #     val = [(0, 0, {
                    #         'product_id': get_product.id,
                    #         'uom_id': get_product.uom_id.id,
                    #         'price_unit': get_product.list_price
                    #     })]
                    #     rec.labour_estimation_ids = val

            #overhead cost
            for mt_line in rec.material_estimation_ids:
                if mt_line.bom_product_id and mt_line.bom_product_id.id not in rec.overhead_estimation_ids.product_id.ids:
                    val = [(0, 0, {
                        'product_id': mt_line.bom_product_id.id,
                        'uom_id': mt_line.bom_product_id.uom_id.id,
                        # 'price_unit': mt_line.bom_product_id.list_price
                    })]
                    rec.overhead_estimation_ids = val
                else:

                    get_oc = rec.overhead_estimation_ids.filtered(
                        lambda x: x.product_id.id == mt_line.bom_product_id.id)
                    get_fp = rec.final_product_ids.filtered(
                        lambda x: x.final_product_id.id == mt_line.bom_product_id.id)
                    get_fp.overhead_cost = get_oc.subtotal
                    get_fp.profit_amount=(get_fp.material_cost + get_fp.labour_cost + get_fp.overhead_cost)*get_single_profit
                    get_fp.amount = get_fp.material_cost + get_fp.labour_cost + get_fp.overhead_cost+ get_fp.profit_amount
                    get_fp.final_amount = get_fp.amount*get_fp.final_quantity

                    # rec.overhead_estimation_ids = [(5, 0, 0)]
                    # product_dict = {}
                    # for mt_line in rec.material_estimation_ids:
                    #     if mt_line.bom_product_id.id not in product_dict.keys():
                    #         product_dict[mt_line.bom_product_id.id] = mt_line.subtotal
                    #     else:
                    #         product_dict[mt_line.bom_product_id.id] += mt_line.subtotal
                    #
                    # for p_dict in product_dict.keys():
                    #     get_product = self.env['product.product'].search([('id', '=', p_dict)])
                    #     val = [(0, 0, {
                    #         'product_id': get_product.id,
                    #         'uom_id': get_product.uom_id.id,
                    #         # 'price_unit': get_product.list_price
                    #     })]
                    #     rec.overhead_estimation_ids = val

    @api.onchange('labour_estimation_ids','overhead_estimation_ids')
    def set_final_product_other_cost(self):
        for rec in self:
            get_total_profit = (rec.total_material_estimate + rec.total_labour_estimate + rec.total_overhead_estimate) * (
                                           rec.profit_percent / 100)
            if (rec.total_material_estimate + rec.total_labour_estimate + rec.total_overhead_estimate)>0:
                get_single_profit = get_total_profit / (rec.total_material_estimate + rec.total_labour_estimate + rec.total_overhead_estimate)
            else:
                get_single_profit=0
            for lb_line in rec.labour_estimation_ids:
                for fp_line in rec.final_product_ids:
                    if lb_line.product_id.id==fp_line.final_product_id.id:
                        fp_line.labour_cost=lb_line.subtotal
                        fp_line.profit_amount=(fp_line.material_cost+fp_line.labour_cost+fp_line.overhead_cost)*get_single_profit
                        fp_line.amount=fp_line.material_cost+fp_line.labour_cost+fp_line.overhead_cost+fp_line.profit_amount
            for oh_line in rec.overhead_estimation_ids:
                for fp_line in rec.final_product_ids:
                    if oh_line.product_id.id==fp_line.final_product_id.id:
                        fp_line.overhead_cost=oh_line.subtotal
                        fp_line.profit_amount = (fp_line.material_cost + fp_line.labour_cost + fp_line.overhead_cost) * get_single_profit
                        fp_line.amount=fp_line.material_cost+fp_line.labour_cost+fp_line.overhead_cost+fp_line.profit_amount


    def action_create_bom(self):
        for rec in self:
            for mt_line in rec.material_estimation_ids:
                if not mt_line.bom_product_id:
                    raise ValidationError(_('Please select BOM Product in every row to create BOM'))

            bom_parent = self.env['mrp.bom'].create({
                'type': 'normal',
                'estimate_id': self.id,
                'project_id': self.project_id.id,
                'partner_id': self.partner_id.id,
            })

            if bom_parent:
                for mt_line in rec.material_estimation_ids:
                    self.env['mrp.bom.line'].create({
                        'bom_product_id': mt_line.bom_product_id.id,
                        'product_id': mt_line.product_id.id,
                        'product_qty': mt_line.quantity,
                        'bom_id': bom_parent.id,
                        'product_uom_id': mt_line.uom_id.id,
                    })
                for bom_line in rec.final_product_ids:
                    self.env['bom.final.product'].create({
                        'final_product_id':bom_line.final_product_id.id,
                        'quantity':bom_line.quantity,
                        'bom_id': bom_parent.id,
                    })

        # if not self.bom_product_id:
        #     raise ValidationError(_('Please select BOM Product to create BOM'))
        # if self.bom_product_id:
        #     bom_id = self.env['mrp.bom'].create({
        #         'product_id': self.bom_product_id.id,
        #         'product_tmpl_id': self.bom_product_id.product_tmpl_id.id,
        #         'product_qty': 1.0,
        #         'type': 'normal',
        #         'estimate_id': self.id,
        #         'project_id': self.project_id.id,
        #         'partner_id': self.partner_id.id,
        #     })
        #     if bom_id:
        #         for line in self.material_estimation_ids:
        #             self.env['mrp.bom.line'].create({
        #                 'product_id': line.product_id.id,
        #                 'product_qty': line.quantity,
        #                 'bom_id': bom_id.id,
        #                 'product_uom_id': line.uom_id.id,
        #             })
        #         for line in self.labour_estimation_ids:
        #             self.env['mrp.bom.line'].create({
        #                 'product_id': line.product_id.id,
        #                 'product_qty': line.hours,
        #                 'bom_id': bom_id.id,
        #                 'product_uom_id': line.uom_id.id,
        #             })
        #         for line in self.overhead_estimation_ids:
        #             self.env['mrp.bom.line'].create({
        #                 'product_id': line.product_id.id,
        #                 'product_qty': line.quantity,
        #                 'bom_id': bom_id.id,
        #                 'product_uom_id': line.uom_id.id,
        #             })

    def action_create_quotation(self):
        order_lines = []
        # for line_ids in {self.material_estimation_ids, self.labour_estimation_ids, self.overhead_estimation_ids}:
        #     for line in line_ids:
        #         order_lines.append((0, 0, {
        #             'name': line.product_id.name,
        #             'product_id': line.product_id.id,
        #             'type': line.type,
        #             'product_uom_qty': line.quantity,
        #             'product_uom': line.uom_id.id,
        #             'price_unit': line.price_unit,
        #             'discount': line.discount,
        #         }))
        material_lines=[]
        # for line in self.material_estimation_ids:
        for rec in self:
            for line in rec.final_product_ids:
                val=(0,0,{
                    'product_id': line.final_product_id.id,
                    'name': line.final_product_id.name,
                    # 'name':self.bom_product_id.description_sale if self.bom_product_id.description_sale else self.bom_product_id.name,
                    'type': 'material',
                    'product_uom_qty': line.final_quantity,
                    'product_uom': line.final_product_id.uom_id.id,
                    'price_unit': line.amount,
                    'price_subtotal': rec.total_job_estimate
                })
                material_lines.append(val)

        # val=(0,0,{
        #     'product_id':self.bom_product_id.id,
        #     'name':self.bom_product_id.name,
        #     # 'name':self.bom_product_id.description_sale if self.bom_product_id.description_sale else self.bom_product_id.name,
        #     'type':'material',
        #     'product_uom_qty':1,
        #     'product_uom':self.bom_product_id.uom_id.id,
        #     'price_unit':self.total_job_estimate,
        #     'price_subtotal':self.total_job_estimate
        # })

        order_id = self.env['sale.order'].create({
            'partner_id': self.partner_id.id or False,
            'state': 'draft',
            'date_order': self.date,
            'user_id': self.sales_person_id.id,
            'company_id': self.company_id.id or False,
            'analytic_account_id': self.analytic_id.id,
            # 'order_line': order_lines,
            'job_estimate_id': self.id,
            'order_line':material_lines
        })
        res = self.write({
            'sale_quotation_id': order_id.id,
            'state': 'done'
        })
        return res