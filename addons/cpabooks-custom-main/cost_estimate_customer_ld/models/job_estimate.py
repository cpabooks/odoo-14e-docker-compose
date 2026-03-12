from odoo import api, fields, models, tools, _
from datetime import datetime

from odoo.exceptions import ValidationError


class JobEstimateCategory(models.Model):
    _name = 'job.estimate.category'
    _description = "Job Estimate Category"

    name = fields.Char(string='Job Name', required=True)


class JobEstimate(models.Model):
    _name = "job.estimate"
    _description = "Job Estimate"
    _inherit = ['mail.thread.cc', 'mail.activity.mixin', 'utm.mixin']

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('job.sequence') or '/'
        vals['user_id'] = self.env.uid
        vals['create_product_variant_id']=None
        get_sequence_app_installed = self.env['ir.module.module'].sudo().search([('name', '=', 'cpabooks_sequences')])
        if get_sequence_app_installed:
            get_sequence = self.env['ir.sequence'].next_by_sequence_for('job_estimation')
            if not get_sequence:
                raise ValidationError(_("Sequence is not set for Job Estimation"))
            vals['name'] = get_sequence or _('/')
        return super(JobEstimate, self).create(vals)


    def write(self, vals):
        if 'create_product_variant_id' in vals.keys():
            vals.pop('create_product_variant_id', None)
        return super(JobEstimate, self).write(vals)
            

    # @api.multi
    def action_job_confirm(self):
        res = self.write({'state': 'confirmed'})
        return res

    # @api.multi
    def action_set_to_draft(self):
        res = self.write({'state': 'draft'})
        return res

    # @api.multi
    def action_cancel(self):
        res = self.write({'state': 'cancel'})
        return res

    # @api.multi
    def action_approve(self):
        res = self.write({'state': 'approved'})
        return res

    # @api.multi
    def action_reject(self):
        res = self.write({'state': 'cancel'})
        return res

    # @api.multi
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
        val=(0,0,{
            'product_id':self.bom_product_id.id,
            'name':self.bom_product_id.name,
            # 'name':self.bom_product_id.description_sale if self.bom_product_id.description_sale else self.bom_product_id.name,
            'type':'material',
            'product_uom_qty':1,
            'product_uom':self.bom_product_id.uom_id.id,
            'price_unit':self.total_job_estimate,
            'price_subtotal':self.total_job_estimate
        })
        material_lines.append(val)
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

    # @api.multi
    def action_send_quotation(self):
        self.ensure_one()
        ir_model_data = self.env['ir.model.data']
        try:
            template_id = \
                ir_model_data.get_object_reference('cost_estimate_customer_ld', 'email_template_job_estimation')[1]
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data.get_object_reference('mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False

        self.estimate_sent = True

        ctx = {
            'default_model': 'job.estimate',
            'default_res_id': self.ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'force_email': True
        }
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }

    @api.depends('labour_estimation_ids.subtotal', 'overhead_estimation_ids.subtotal',
                 'material_estimation_ids.subtotal', 'profit_percent')
    def _compute_total_job_estimate(self):
        for order in self:
            for line in order.labour_estimation_ids:
                labour_price = (line.quantity * line.price_unit * line.hours) - (
                        line.quantity * line.price_unit * line.hours) * (line.discount or 0.0) / 100.0
                order.total_labour_estimate += labour_price

            for line in order.overhead_estimation_ids:
                overhead_price = (line.quantity * line.price_unit) - (line.quantity * line.price_unit) * (
                        line.discount or 0.0) / 100.0
                order.total_overhead_estimate += overhead_price

            for line in order.material_estimation_ids:
                material_price = (line.quantity * line.price_unit) - (line.quantity * line.price_unit) * (
                        line.discount or 0.0) / 100.0
                order.total_material_estimate += material_price
            total = order.total_labour_estimate + order.total_overhead_estimate + order.total_material_estimate
            if order.profit_percent != 0:
                order.total_job_estimate = total + (total * order.profit_percent / 100)
            else:
                order.total_job_estimate = total

    def _compute_quotation_count(self):
        for sale in self:
            sale_ids = self.env['sale.order'].search([('job_estimate_id', '=', sale.id)])
            sale.internal_quotation_count = len(sale_ids)
        return True

    def action_view_quotations(self):
        self.ensure_one()
        return {
            'name': 'Quotation',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'sale.order',
            'domain': [('job_estimate_id', '=', self.id)],
        }

    @api.onchange('company_id')
    def get_previous_template(self):
        get_previous = self.env['job.estimate'].sudo().search([('company_id', '=', self.company_id.id)],limit=1,order='id desc')
        self.style = get_previous.style


    name = fields.Char(string='Number', readonly=True, copy=False)
    partner_id = fields.Many2one('res.partner', 'Customer', required=True)
    state = fields.Selection(
        [('draft', 'Draft'), ('confirmed', 'Confirmed'), ('approved', 'Approved'),
         ('done', 'Quotation Created'), ('cancel', 'Cancel')], 'Status', default="draft")
    date = fields.Date('Date', required=True, default=datetime.now().date())

    total_labour_estimate = fields.Float(compute='_compute_total_job_estimate', string='Labour Estimation',
                                         readonly=True)
    total_overhead_estimate = fields.Float(compute='_compute_total_job_estimate', string='Overhead Estimation',
                                           readonly=True)
    total_job_estimate = fields.Float(compute='_compute_total_job_estimate', string='Total Job Estimate',
                                      readonly=True)
    customer_ref = fields.Char('Customer Reference')
    internal_quotation_count = fields.Integer('quotation', compute='_compute_quotation_count')

    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id)
    project_id = fields.Many2one('project.project', 'Project')
    analytic_id = fields.Many2one('account.analytic.account', 'Analytic Account')
    job_type_id = fields.Many2many('job.estimate.category', column1='partner_id', column2='category_id',
                                   string='Job Type')
    payment_term_id = fields.Many2one('account.payment.term', 'Payment Terms')
    sales_person_id = fields.Many2one('res.users', 'Salesman')
    sales_team_id = fields.Many2one('crm.team', 'Sales Team')
    sale_quotation_id = fields.Many2one('sale.order', 'Sales Quotation', readonly=True)
    user_id = fields.Many2one('res.users', string="User")

    material_estimation_ids = fields.One2many('material.estimate', 'material_id', 'Material Estimation',copy=True)
    labour_estimation_ids = fields.One2many('labour.estimate', 'labour_id', 'Labour Estimation',copy=True)
    overhead_estimation_ids = fields.One2many('overhead.estimate', 'overhead_id', 'Overhead Estimation',copy=True)
    description = fields.Text('Description')
    total_material_estimate = fields.Float(compute='_compute_total_job_estimate', string='Total Material Estimate',
                                           readonly=True)

    profit_percent = fields.Float(string='Profit %')
    estimate_sent = fields.Boolean()
    create_product_variant_id=fields.Many2one('product.template', string="Create Product Variants")
    style = fields.Selection(
        [
            ('ESTIMATION_0_document','Estimate Default Template'),
            ('ESTIMATION_common_document','Estimate Common Template'),
        ],
        'PDF Template', default='ESTIMATION_common_document',
        help="Select Style to use when printing the Sales Job Estimate")
