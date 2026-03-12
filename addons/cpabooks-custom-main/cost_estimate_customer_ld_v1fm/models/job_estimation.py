from odoo import api, fields, models, tools, _
from datetime import datetime

from odoo.exceptions import ValidationError


class JobEstimate(models.Model):
    _inherit = "job.estimate"

    total_profit_amount = fields.Float(compute='_compute_total_job_estimate', string='Total Profit Amount',
                                      readonly=True)
    total_discount_amount=fields.Float(compute='_compute_total_job_estimate', string='Total Material Discount Amount',
                                      readonly=True)
    final_total_material_amount=fields.Float(compute='_compute_total_job_estimate', string='Total Material Discount Amount',
                                      readonly=True)

    @api.depends('labour_estimation_ids.subtotal', 'overhead_estimation_ids.subtotal',
                 'material_estimation_ids.subtotal', 'profit_percent')
    def _compute_total_job_estimate(self):
        for order in self:
            for line in order.labour_estimation_ids:
                labour_price = (line.quantity * line.price_unit * line.hours) - (
                        line.quantity * line.price_unit * line.hours) * (line.discount or 0.0) / 100.0
                order.total_labour_estimate += labour_price

            for line in order.material_estimation_ids:
                overhead_price = (line.quantity * line.price_unit) * (line.overhead_per / 100)
                order.total_overhead_estimate += overhead_price

            for line in order.material_estimation_ids:
                profit_amount = (line.quantity * line.price_unit) * (line.profit_per / 100)
                order.total_profit_amount += profit_amount

            for line in order.material_estimation_ids:
                discount_amount = (((line.quantity * line.price_unit) + line.profit_amount + line.overhead_amount) * (
                            (line.discount or 0.0) / 100.0))
                order.total_discount_amount += discount_amount

            for line in order.material_estimation_ids:
                material_price = (line.quantity * line.price_unit)
                order.total_material_estimate += material_price
            order.final_total_material_amount= order.total_material_estimate + order.total_profit_amount - order.total_discount_amount
            total = order.total_labour_estimate + order.total_overhead_estimate + order.total_material_estimate + order.total_profit_amount - order.total_discount_amount
            if order.profit_percent != 0:
                order.total_job_estimate = total + (total * order.profit_percent / 100)
            else:
                order.total_job_estimate = total


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
        for line in self.material_estimation_ids:
            if not line.description:
                raise ValidationError(_("Description is required, Product:\n"+line.product_id.name))
            val=(0,0,{
                'product_id':line.product_id.id,
                'name':line.description,
                # 'name':line.product_id.description_sale if line.product_id.description_sale else line.product_id.name,
                'type':'material',
                'product_uom_qty':line.quantity,
                'product_uom':line.product_id.uom_id.id,
                'price_unit':line.subtotal/line.quantity,
                'price_subtotal':line.subtotal
            })
            material_lines.append(val)
        order_id = self.env['sale.order'].create({
            'partner_id': self.partner_id.id or False,
            'state': 'draft',
            'date_order': datetime.now().date(),
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

