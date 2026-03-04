from odoo import api, models, fields, _


class ProjectTask(models.Model):
    _inherit = 'project.task'

    sample = fields.Char('Sample')
    close_remarks = fields.Text('Closing Remarks')
    complaint_title = fields.Many2one('complaint.detail','Complaint Title')
    complaint_details = fields.Text('Complaint Details')
    client_person = fields.Many2one('contact.person', 'Contact Person')
    client_contact = fields.Char('Contact Number')
    site_location = fields.Many2one('site.location', 'Site Location')
    client_email = fields.Char('Email ID')
    qt_no = fields.Many2one('sale.order', string='Ref Quotation No.')
    check_fsm = fields.Boolean('Check FSM', default=True)
    complaint_type = fields.Selection([
        ('amc','AMC'),
        ('warranty_service', 'Warranty/Service'),
        ('new_installation', 'New Installation'),
        ('new_inquiry', 'New Inquiry'),
    ], 'Complaint Type')
    total_print_row = fields.Integer(default=5, string="Total Print Row")
    invoice_id = fields.Many2one('account.move', 'Ref. Invoice No.', domain=[('move_type', '=', 'out_invoice')])
    # invoice_type = fields.Char(related='invoice_id.x_studio_invoice_type', string='Invoice Type', readonly=True)
    item_des = fields.Many2one(
        'account.move.line',
        string='Invoice Line',
        domain="""
                [
                    ('move_id', '=', invoice_id),
                    ('display_type', '=', False),
                    ('product_id', '!=', False)
                ]
            """
    )
    stage = fields.Selection([
        ('registered', '1. Registered'),
        ('site_visited', '2. Site Visited (i)'),
        ('qty_issued','3. Qtn Issued and waiting for Approval'),
        ('qty_approved','4. QTN Approved'),
        ('in_progress','5. Work in Progress'),
        ('waiting_for_invoice','6. Job Complete Waiting for Invoice'),
        ('job_completed','7. Job Completed‐ FOC'),
        ('job_completed_invoiced','8. Job Completed & Invoiced'),
        ('approved','9. Approved'),
    ], string='Stage', default='registered', tracking=True)
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
    select_invoice = fields.Many2one('account.move', string='Select Invoice',
                                     domain=[('move_type', '=', 'out_invoice')])

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

    @api.onchange('visited_by', 'next_action', 'work_completion')
    def _onchange_stage_logic(self):
        for rec in self:
            # 4️⃣ Work completed → highest priority
            if rec.work_completion == 'invoiced' or rec.work_completion == 'foc':
                rec.stage = 'job_completed'

            elif rec.sale_order_id.state == 'draft':
                rec.stage = 'qty_issued'

            # 3️⃣ Remarks closed
            elif rec.next_action == 'closed':
                rec.stage = 'job_completed'

            # 2️⃣ Remarks issue / foc
            elif rec.next_action in ('issue', 'foc'):
                rec.stage = 'in_progress'

            # 1️⃣ Visited
            elif rec.visited_by:
                rec.stage = 'site_visited'
