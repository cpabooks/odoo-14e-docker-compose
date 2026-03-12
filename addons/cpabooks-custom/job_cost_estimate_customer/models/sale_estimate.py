# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError,AccessError,Warning
import odoo.addons.decimal_precision as dp
from odoo import SUPERUSER_ID




class SaleEstimateJob(models.Model):
    _name = "sale.estimate.job"
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin'] #odoo11
    _description = "Sales Estimate Job"
    _rec_name = 'number'
    _order = 'id desc'
    
    number = fields.Char(
        'Number',
        copy=False,
    )
    estimate_date = fields.Date(
        'Date',
        required=True,
        copy=False,
        default = fields.date.today(),
    )
    partner_id = fields.Many2one(
        'res.partner',
        string='Customer',
        required=True,
    )
    company_id = fields.Many2one(
        'res.company',
        required=True,
        default=lambda self: self.env.user.company_id,
        string='Company',
    )
    state = fields.Selection([
        ('draft', 'Draft'),
        ('sent', 'Estimate Sent'),
        ('confirm', 'Confirmed'),
        ('approve', 'Approved'),
        ('reject', 'Rejected'),
        ('quotesend', 'Quotation Created'),
        ('cancel', 'Cancelled')],
        default='draft',
        track_visibility='onchange',
        copy='False',
    )
    pricelist_id = fields.Many2one(
        'product.pricelist', 
        string='Pricelist', 
        required=True, 
        help="Pricelist for current sales estimate."
    )
    payment_term_id = fields.Many2one(
        'account.payment.term', 
        string='Payment Terms', 
        oldname='payment_term'
    )
    description = fields.Text(
        string='Description of Work'
    )
    note = fields.Text(
        string='Note'
    )
    currency_id = fields.Many2one(
        "res.currency", 
        related='pricelist_id.currency_id', 
        string="Currency", 
        readonly=True, 
        #required=True,
        store=True,
    )
    estimate_ids = fields.One2many(
        'sale.estimate.line.job',
        'estimate_id',
        'Estimate Lines',
        copy=True,
        domain=[('job_type','=','material')],
    )
    reference = fields.Char(
        string='Customer Reference'
    )
    source = fields.Char(
        string='Source Document'
    )
    total = fields.Float(
        compute='_compute_totalestimate', 
        string='Total Material Estimate', 
        store=True
    )
    user_id = fields.Many2one(
        'res.users',
        'Sales Person',
        default=lambda self: self.env.user,
    )
    team_id = fields.Many2one(
        'crm.team',
        'Sales Team',
    )
    quotation_id = fields.Many2one(
        'sale.order',
        'Sales Quotation',
        readonly=True,
        copy=False,
    )

    
    @api.depends(
        'total',
        'labour_total',
        'overhead_total'
    )
    def _compute_job_estimate_total(self):
        for rec in self:
            rec.estimate_total = rec.total + rec.labour_total + rec.overhead_total
            
    @api.depends('labour_estimate_line_ids.price_subtotal')
    def _compute_labour_total(self):
        for rec in self:
            rec.labour_total = 0.0
            for line in rec.labour_estimate_line_ids:
                rec.labour_total += line.price_subtotal
                
    @api.depends('overhead_estimate_line_ids.price_subtotal')
    def _compute_overhead_total(self):
        for rec in self:
            rec.overhead_total = 0.0
            for line in rec.overhead_estimate_line_ids:
                rec.overhead_total += line.price_subtotal

    project_id = fields.Many2one(
        'project.project',
        string="Project"
    )
    labour_estimate_line_ids = fields.One2many(
        'sale.estimate.line.job',
        'estimate_id',
        copy=True,
        domain=[('job_type','=','labour')],
    )
    overhead_estimate_line_ids = fields.One2many(
        'sale.estimate.line.job',
        'estimate_id',
        copy=True,
        domain=[('job_type','=','overhead')],
    )
    analytic_id = fields.Many2one(
        'account.analytic.account',
        string='Analytic Account',
        store=True,
        related="project_id.analytic_account_id",
    )
    labour_total = fields.Float(
        compute='_compute_labour_total', 
        string='Total Labour Estimate', 
        store=True
    )
    overhead_total = fields.Float(
        compute='_compute_overhead_total', 
        string='Total Overhead Estimate', 
        store=True
    )
    estimate_total = fields.Float(
        string='Total Job Estimate',
        compute='_compute_job_estimate_total',
        store=True,
    )
    job_type_ids = fields.Many2many(
        'estimate.job.type',
        string='Job Types',
    )

    employee_id = fields.Many2one(
        'hr.employee',
        string='Technical Person Incharge',
    )



    @api.depends('estimate_ids.price_subtotal')
    def _compute_totalestimate(self):
        for rec in self:
            rec.total = 0.0
            for line in rec.estimate_ids:
                rec.total += line.price_subtotal


    @api.onchange('partner_id')
    def _onchange_customer_id(self):
        for rec in self:
            partner = self.env['res.partner'].browse(rec.partner_id.id)
            rec.pricelist_id = partner.property_product_pricelist.id
            rec.payment_term_id = partner.property_payment_term_id.id
            rec.reference = partner.ref
            
    # @api.multi
    def estimate_send(self):
        for rec in self:
            rec.state = 'sent'
            
    # @api.multi
    def estimate_confirm(self):
        for rec in self:

            # if not rec.estimate_ids:
            # if not rec.estimate_ids and not rec.labour_estimate_line_ids and not rec.overhead_estimate_line_ids:
            #     raise UserError(_('Please enter Estimation Lines!'))
            rec.state = 'confirm'
            
    # @api.multi
    def estimate_approve(self):
        su_id = self.env['res.users'].browse(SUPERUSER_ID)
        users = self.env['res.users'].search(
            [('groups_id', 'in', [self.env.ref('job_cost_estimate_customer.group_estimate_approve_user').id])])

        for rec in self:
            if not self.env.user.has_group('job_cost_estimate_customer.group_estimate_approve_user'):
                template_id = self.env.ref('job_cost_estimate_customer.access_denied_mail')
                # email_values = {'email_to': rec.partner_id.email,
                #                 'email_from': self.env.user.email}
                for i in users:
                    email_values = {'email_to': i.partner_id.email,
                                    'email_from': self.env.user.email,
                                        # su_id.partner_id.email
                                    }
                    template_id.send_mail(rec.id, email_values=email_values,force_send=True)
                raise Warning(_("Thank you for your effort, your estimate is sent for approval. Once approved, you will be notified."))

                # raise UserError(_("Thank you for your effort, your estimate is sent for approval. Once approved, you will be notified."))
                # raise AccessError(_("Thank you for your effort, your estimate is sent for approval. Once approved, you will be notified."))
            else:
                return {
                    'name': 'Are you sure?',
                    'type': 'ir.actions.act_window',
                    'res_model': 'approval.message',
                    'view_mode': 'form',
                    'view_type': 'form',
                    'target': 'new',
                    'context': {'current_id': self.id}
                }
                # rec.state = 'approve'
            
    # @api.multi
    def estimate_quotesend(self):
        for rec in self:
            rec.state = 'quotesend'
            
    # @api.multi
    def estimate_cancel(self):
        for rec in self:
            rec.state = 'cancel'
        
    # @api.multi
    def estimate_reject(self):
        for rec in self:
            rec.state = 'reject'
            
    # @api.multi
    def reset_todraft(self):
        for rec in self:
            rec.state = 'draft'

    def btn_reverse(self):
        su_id = self.env['res.users'].browse(SUPERUSER_ID)
        for rec in self:
            rec.state = 'draft'
            template_id = self.env.ref('job_cost_estimate_customer.revised_mail')
            email_values = {'email_to': rec.user_id.partner_id.email,
                            'email_from': self.env.user.email,
                                # su_id.partner_id.email
                            }
            template_id.send_mail(rec.id, email_values=email_values, force_send=True)


            
    @api.model
    def create(self, vals):
        number = self.env['ir.sequence'].next_by_code('product.estimate.seq.job')
        vals.update({
            'number': number
            })
        res = super(SaleEstimateJob, self).create(vals)
        return res
        
    # @api.multi
    def action_estimate_send(self):
        if self.state == 'sent' or self.state == 'approve' or self.state == 'quotesend' or self.state == 'confirm':
            '''
            This function opens a window to compose an email, with the edi sale template message loaded by default
            '''
            #self.state = 'sent'
            self.ensure_one()
            ir_model_data = self.env['ir.model.data']
            try:
                template_id = ir_model_data.get_object_reference('job_cost_estimate_customer', 'email_template_estimate_job')[1]
            except ValueError:
                template_id = False
            try:
                compose_form_id = ir_model_data.get_object_reference('mail', 'email_compose_message_wizard_form')[1]
            except ValueError:
                compose_form_id = False
            ctx = dict()
            ctx.update({
                'default_model': 'sale.estimate.job',
                'default_res_id': self.ids[0],
                'default_use_template': bool(template_id),
                'default_template_id': template_id,
                'default_composition_mode': 'comment',
                'mark_so_as_sent': True,
                #'custom_layout': "sale.mail_template_data_notification_email_sale_order"
            })
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
        if self.state == 'draft':
            '''
            This function opens a window to compose an email, with the edi sale template message loaded by default
            '''
            self.state = 'sent'
            self.ensure_one()
            ir_model_data = self.env['ir.model.data']
            try:
                template_id = ir_model_data.get_object_reference('job_cost_estimate_customer', 'email_template_estimate_job')[1]
            except ValueError:
                template_id = False
            try:
                compose_form_id = ir_model_data.get_object_reference('mail', 'email_compose_message_wizard_form')[1]
            except ValueError:
                compose_form_id = False
            ctx = dict()
            ctx.update({
                'default_model': 'sale.estimate.job',
                'default_res_id': self.ids[0],
                'default_use_template': bool(template_id),
                'default_template_id': template_id,
                'default_composition_mode': 'comment',
                'mark_so_as_sent': True,
                #'custom_layout': "sale.mail_template_data_notification_email_sale_order"
            })
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
        
    # @api.multi
    def _prepare_quotation_line(self,quotation):
        quo_line_obj = self.env['sale.order.line']
        # return

        
    # @api.multi
    def estimate_to_quotation(self):
        quo_obj = self.env['sale.order']
        quo_line_obj = self.env['sale.order.line']
        for rec in self:
            vals = {
                'partner_id':rec.partner_id.id,
                'origin': rec.number,
                'estimate_id':rec.id,
                # 'project_id':rec.analytic_id.id
                'analytic_account_id':rec.analytic_id.id,
                'payment_term_id':rec.payment_term_id.id,
                'markup': rec.markup,
                'customer_code':rec.partner_id.ref,
                'note':rec.description,
                # 'reference':rec.partner_id.ref,

                }
            quotation = quo_obj.create(vals)
            rec._prepare_quotation_line(quotation)
            rec.quotation_id = quotation.id
        rec.state = 'quotesend'



class confirm_approve(models.TransientModel):
    _name = 'approval.message'


    text= fields.Char(string="NOTE")

    def btn_approve(self):
        current_id = self.env.context.get('current_id', False)
        estimate = self.env['sale.estimate.job'].browse(current_id)
        su_id = self.env['res.users'].browse(SUPERUSER_ID)

        for order in estimate:
            order.write({'state': 'approve',})
            partner = self.env.user.partner_id
            # order.sudo().message_post(body=self.text, message_type='notification', author_id=partner.id)
            partner_ids = [order.partner_id.id]
            order.sudo().message_post(body=self.text, message_type='comment', partner_ids=partner_ids)
            template_id = self.env.ref('job_cost_estimate_customer.approve_mail')
            email_values = {'email_to': order.user_id.partner_id.email,
                            'email_from': self.env.user.email,
                                # su_id.partner_id.email
                            }
            template_id.send_mail(order.id, email_values=email_values, force_send=True)
        return



# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
