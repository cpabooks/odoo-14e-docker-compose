from odoo import api, models, fields, _


class ProjectTask(models.Model):
    _inherit = 'project.task'
    _rec_name = 'task_seq'

    sample = fields.Char('Sample')
    close_remarks = fields.Text('Closing Remarks')
    complaint_title = fields.Many2one('complaint.detail', 'Complaint Title')
    complaint_details = fields.Text('Complaint Details')
    client_person = fields.Many2one('contact.person', 'Contact Person')
    client_contact = fields.Char('Contact Number')
    site_location = fields.Many2one('site.location', 'Site Location')
    client_email = fields.Char('Email ID')
    qt_no = fields.Many2one('sale.order', string='Ref Quotation No.')
    check_fsm = fields.Boolean('Check FSM', default=True)
    complaint_type = fields.Selection([
        ('amc', 'AMC'),
        ('warranty_service', 'Warranty/Service'),
        ('new_installation', 'New Installation'),
        ('new_inquiry', 'New Inquiry'),
    ], 'Complaint Type')
    total_print_row = fields.Integer(default=10, string="Total Print Row")
    invoice_id = fields.Many2one('account.move', 'Ref. Invoice No.', domain=[('move_type', '=', 'out_invoice')])
    invoice_type = fields.Char(compute="_compute_invoice_type", string='Invoice Type', readonly=True)
    item_des = fields.Many2one(
        'account.move.line',
        string='Invoice Line',
        domain="""
                [
                    ('move_id', '=', invoice_id),
                    ('display_type', '=', False),
                    ('product_id', '!=', False),
                    ('guaranteed', '=', True)
                ]
            """
    )
    stage = fields.Selection([
        ('registered', '1. Registered'),
        ('site_visited', '2. Site Visited (i)'),
        ('qty_issued', '3. Qtn Issued and waiting for Approval'),
        ('qty_approved', '4. QTN Approved'),
        ('in_progress', '5. Work in Progress'),
        ('waiting_for_invoice', '6. Job Complete Waiting for Invoice'),
        ('job_completed', '7. Job Completed‐FOC'),
        ('job_completed_invoiced', '8. Job Completed & Invoiced'),
        ('approved', '9. Approved'),
    ], string='Stage', default='registered', tracking=True, compute="_compute_stage_logic", search="_search_stage")
    site_visit = fields.Text('Site Visit Remarks')
    visited_by = fields.Many2one('hr.employee', 'Visited By')
    visited_date = fields.Date('Visited Date')
    material_line_ids = fields.One2many(
        'material.request.line',
        'task_id',
    )
    work_completion = fields.Selection([('invoiced', 'Invoiced'), ('foc', 'FOC Done')], string='iv. Work Completion:')
    closing_remarks = fields.Text('Closing Remarks')
    approved_by = fields.Many2one(
        'res.users',
        string='Approved By',
        ondelete='set null'
    )
    select_invoice = fields.Many2one('account.move', string='Select Invoice', compute="_compute_select_invoice")

    next_action = fields.Selection([
        ('closed', '1. Closed'),
        ('issue', '2. Issue QT'),
        ('foc', '3. FOC'),
    ], string='Next Action', tracking=True)
    assign_date = fields.Date(string='Assign Date')
    crn_done_before = fields.Char('CRN Done Before', readonly=True)

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        if 'user_id' in res:
            res['user_id'] = False
        res['name'] = "Field Service Task"
        return res

    @api.onchange('item_des')
    def _compute_crn_done_before(self):
        for rec in self:
            if rec.item_des:
                similar_tasks = self.env['project.task'].search([('item_des', '=', rec.item_des.id)], limit=1)
                if similar_tasks:
                    rec.crn_done_before = similar_tasks.task_seq
                else:
                    rec.crn_done_before = False

    @api.depends('remarks')
    def _compute_date_end(self):
        for rec in self:
            if rec.remarks == 'closed':
                rec.date_end = fields.Date.today()
            else:
                rec.date_end = False

    @api.depends('visited_by', 'next_action', 'assign_date', 'date_end', 'select_invoice', 'user_id')
    def _compute_stage_logic(self):
        for rec in self:
            # Save the current stage so we don't accidentally wipe manual changes
            current_stage = rec.stage or 'registered'

            if rec.next_action == 'closed' or (rec.next_action == 'foc' and rec.date_end):
                rec.stage = 'job_completed'
            elif rec.select_invoice:
                rec.stage = 'job_completed_invoiced'
            elif rec.next_action == 'issue' and rec.date_end:
                rec.stage = 'waiting_for_invoice'
            elif rec.user_id or rec.assign_date:
                rec.stage = 'in_progress'
            elif rec.visited_by:
                rec.stage = 'site_visited'
            else:
                rec.stage = current_stage

    def _search_stage(self, operator, value):
        """
        Custom search method to allow filtering by the non-stored 'stage' computed field.
        Returns a domain of matching IDs.
        """
        # Fetch all tasks (or optimize by searching active=True depending on your needs)
        tasks = self.env['project.task'].with_context(prefetch_fields=False).search([])

        # Filter records in Python memory based on the requested operator
        if operator == '=':
            matching_ids = tasks.filtered(lambda t: t.stage == value).ids
        elif operator == '!=':
            matching_ids = tasks.filtered(lambda t: t.stage != value).ids
        elif operator == 'in':
            matching_ids = tasks.filtered(lambda t: t.stage in value).ids
        elif operator == 'not in':
            matching_ids = tasks.filtered(lambda t: t.stage not in value).ids
        else:
            # Fallback for unsupported operators (like 'ilike' for selections)
            matching_ids = []

        # Return a standard Odoo domain containing the matching record IDs
        return [('id', 'in', matching_ids)]

    @api.depends('invoice_id.invoice_type')
    def _compute_invoice_type(self):
        for rec in self:
            if rec.invoice_id:
                rec.invoice_type = rec.invoice_id.invoice_type.name
            else:
                rec.invoice_type = False

    @api.onchange('invoice_id')
    def _onchange_invoice_id(self):
        if self.invoice_id and self.invoice_id.project_id:
            self.project_id = self.invoice_id.project_id
        else:
            self.project_id = False

    def _compute_select_invoice(self):
        for rec in self:
            rec.select_invoice = False
            # We use the new sale_order_ids relation to find invoices.
            # This allows Odoo to automatically trigger this function when an invoice is posted!
            so = self.env['sale.order'].search([('task_id', '=', rec.id)], limit=1)
            if so:
                # Find all invoices linked to this sale order that are posted customer invoices
                posted_invoices = so.invoice_ids.filtered(
                    lambda inv: inv.state == 'posted' and inv.move_type == 'out_invoice'
                )
                # Assign the first posted invoice if it exists, otherwise False
                rec.select_invoice = posted_invoices[0].id if posted_invoices else False

    def action_approve_task(self):
        self.write({'stage': 'approved'})
