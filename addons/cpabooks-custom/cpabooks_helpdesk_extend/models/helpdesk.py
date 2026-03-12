import datetime
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError, UserError
from datetime import datetime, date
from odoo.tools import plaintext2html


class HelpdeskExtend(models.Model):
    _inherit = 'helpdesk.ticket'

    name = fields.Char(string='Subject', required=False, index=True)
    module = fields.Many2many('ir.module.module', string='Modules')
    project = fields.Many2one('project.project', string="Project", related='project_id')
    ticket_date = fields.Date(string="Ticket Date", default=datetime.today())
    main_sub_id = fields.Many2one('product.product', string="Main Subject", domain="[('type','=','service')]")
    require_items = fields.One2many('require.items', 'ticket_id', string="Require Items")
    job_closing_date = fields.Date(string="Job Closing Date")
    customer_name = fields.Many2one('res.partner', string="Customer Name")

    issue_description = fields.Text('Issue Description', compute="get_issue_description")
    tasks = fields.Text("Task", compute="get_issue_description")
    # default_issue_description=fields.Many2many('helpdesk.ticket',compute="get_issue")

    ticket_type_id = fields.Many2one('helpdesk.ticket.type', string="Ticket Type",
                                     default=lambda self: self.env['helpdesk.ticket.type'].search(
                                         [('name', '=ilike', 'Customization')], limit=1))
    # module_names = fields.Char('Module Names', compute="compute_module_names", store=True)
    ticket_age = fields.Integer(compute="get_ticket_age", string="Ticket Age")
    dev_name = fields.Many2one('res.partner', string="Dev. Name Portal")
    dev_email = fields.Char(string="Dev. Email Portal")

    des_tree = fields.Text('Description')  # , default=lambda self: self._list_view()
    dis_name = fields.Char('Ticket Name')  # , compute='_get_display_name'
    dev = fields.Many2one('hr.employee', 'Dev. Name')
    # email = fields.Char('Dev. eMail_x')
    email_id = fields.Char('Dev. eMail')
    sub_task = fields.Many2one('project.task', 'Sub Task', compute='_get_sub_task')
    module_id = fields.Many2one('ir.module.module', 'Required Module')

    partner_name = fields.Char(string='Customer Cont. Name', compute='_compute_partner_info', store=True,
                               readonly=False)
    dev_tester = fields.Many2one('res.users', 'Dev. Tester')
    clint_updater = fields.Many2one('res.users', 'Client Updater')
    description_lines = fields.One2many('helpdesk.description.line', 'description_id', 'Descriptions')
    is_list = fields.Boolean('List_view', default=True)
    # total Plan_time
    total_proposed_hour = fields.Float('Total Proposed Hours', defatul=0.00, compute='_compute_total_proposed_hours')

    # plan_time = fields.Float('PT')

    def set_to_draft(self):
        for rec in self:
            rec.ticket_state = "draft"
            stage = self.env['helpdesk.stage'].search([('ticket_state', '=', rec.ticket_state)], limit=1)
            rec.stage_id = stage.id

    @api.depends('timesheet_ids')
    def _compute_total_proposed_hours(self):
        for ticket in self:
            ticket.total_proposed_hour = round(sum(ticket.timesheet_ids.mapped('plan_time')), 2) or 0

    @api.onchange('company_id')
    def get_default_list(self):
        for rec in self:
            get_last = self.env['helpdesk.ticket'].sudo().search(
                [
                    ('company_id', '=', rec.company_id.id)
                ],
                limit=1
            )
            rec.is_list = get_last.is_list if get_last else True

    def action_cancel(self):
        for rec in self:
            rec.ticket_state = "cancel"
            stage = self.env['helpdesk.stage'].search([('ticket_state', '=', rec.ticket_state)], limit=1)
            rec.stage_id = stage.id

    def action_return_draft(self):
        for rec in self:
            rec.ticket_state = "draft"
            stage = self.env['helpdesk.stage'].search([('ticket_state', '=', rec.ticket_state)], limit=1)
            rec.stage_id = stage.id

    def assign_dev(self):
        for rec in self:
            rec.ticket_state = "dev"
            stage = self.env['helpdesk.stage'].search([('ticket_state', '=', rec.ticket_state)], limit=1)
            rec.stage_id = stage.id

    def assign_dev_approve(self):
        for rec in self:
            rec.ticket_state = "dev"
            stage = self.env['helpdesk.stage'].search([('ticket_state', '=', rec.ticket_state)], limit=1)
            rec.stage_id = stage.id

    def send_to_review(self):
        for rec in self:
            rec.ticket_state = "draft"
            stage = self.env['helpdesk.stage'].search([('ticket_state', '=', rec.ticket_state)], limit=1)
            rec.stage_id = stage.id

    def re_assign_developer(self):
        for rec in self:
            rec.ticket_state = "dev"
            stage = self.env['helpdesk.stage'].search([('ticket_state', '=', rec.ticket_state)], limit=1)
            rec.stage_id = stage.id

    def send_to_updater(self):
        for rec in self:
            rec.ticket_state = "updating"
            stage = self.env['helpdesk.stage'].search([('ticket_state', '=', rec.ticket_state)], limit=1)
            rec.stage_id = stage.id

    def send_to_clint(self):
        for rec in self:
            rec.ticket_state = "done"
            rec.job_closing_date = datetime.today()
            stage = self.env['helpdesk.stage'].search([('ticket_state', '=', rec.ticket_state)], limit=1)
            rec.stage_id = stage.id

    def send_to_dev(self):
        for rec in self:
            rec.ticket_state = "dev"
            stage = self.env['helpdesk.stage'].search([('ticket_state', '=', rec.ticket_state)], limit=1)
            rec.stage_id = stage.id

    def send_to_test(self):
        for rec in self:
            rec.ticket_state = "test"
            stage = self.env['helpdesk.stage'].search([('ticket_state', '=', rec.ticket_state)], limit=1)
            rec.stage_id = stage.id

    @api.onchange('company_id')
    def get_default_clint_updater(self):
        context = self._context
        uid = context.get('uid')
        self.clint_updater = uid

    @api.onchange('company_id')
    def get_default_dev_tester(self):
        get_last_dev_tester = self.env['helpdesk.ticket'].sudo().search(
            [('company_id', '=', self.company_id.id)],
            limit=1)
        if get_last_dev_tester:
            self.dev_tester = get_last_dev_tester.dev_tester

    def set_plan(self):
        action = self.env.ref('cpabooks_navbar.planning_popup_action').read()[0]
        action['context'] = {
            'default_employee_id': self.dev.id,
            'default_task_id': self.task_id.id,
            'default_allocated_hours': 1,
        }
        return action

    @api.onchange('dev')
    def get_email_id(self):
        for rec in self:
            rec.email_id = rec.dev.work_email

    def _get_sub_task(self):
        for rec in self:
            if rec.timesheet_ids:
                rec.sub_task = rec.timesheet_ids.sub_task
            else:
                rec.sub_task = False

    # def _get_display_name(self):
    #     max = 70
    #     for rec in self:
    #         if rec.display_name:
    #             rec.dis_name = rec.display_name[:max]
    #         else:
    #             rec.dis_name = False

    def list_view(self):
        max = 20
        name_len = 70
        for record in self:
            record.des_tree = record.description[:max] if record.description else False
            record.dis_name = record.name[:name_len] if record.name else False
            record.is_list = True

    # def _list_view(self):
    #     max = 20
    #     for record in self:
    #         record.des_tree = record.description[:max] if record.description else False
    #         return record.des_tree

    def wrap_view(self):
        max_length = 60
        name_len = 50
        for record in self:
            record.is_list = False
            if record.description:
                # Wrap description if length exceeds max_length
                if len(record.description) > max_length:
                    record.des_tree = "\n".join(
                        [record.description[i:i + max_length] for i in range(0, len(record.description), max_length)])
                else:
                    record.des_tree = record.description
            record.dis_name = record.name[:name_len] if record.name else False

    # def _get_des_tree(self):
    #     max = 70
    #     for record in self:
    #         if record.description:
    #             record.des_tree = record.description[:max]
    #         else:
    #             record.des_tree = False

    @api.onchange('dev_name')
    def set_dev_email(self):
        for rec in self:
            rec.dev_email = rec.dev_name.email

    @api.depends('name')
    def get_ticket_age(self):
        for rec in self:
            days_difference = (fields.Date.today() - rec.ticket_date).days
            rec.ticket_age = days_difference

    @api.depends('require_items')
    def get_issue_description(self):
        for rec in self:
            iss_des = ""
            task_des = ""
            for iss_d in rec.require_items:
                if not iss_des:
                    iss_des = iss_d.description if isinstance(iss_d.description, str) else ""
                else:
                    iss_des += "\n" + iss_d.description if isinstance(iss_d.description, str) else ""
                if not task_des:
                    task_des = iss_d.task_id.name if isinstance(iss_d.task_id.name, str) else ""
                else:
                    task_des += "\n" + iss_d.task_id.name if isinstance(iss_d.task_id.name, str) else ""
            rec.issue_description = iss_des
            rec.tasks = task_des

    # @api.depends('module')
    # def compute_module_names(self):
    #     for rec in self:
    #         if rec.module:
    #             module_names = ','.join([p.shortdesc for p in rec.module])
    #         else:
    #             module_names = ''
    #
    #         rec.module_names = module_names

    @api.onchange('main_sub_id')
    def set_subject(self):
        for rec in self:
            rec.name = rec.main_sub_id.name

    @api.onchange('require_items')
    def set_timesheet(self):
        for rec in self:
            timesheet_vals = []
            helpdesk_ticket_exists = False
            # for time in rec.timesheet_ids:
            #     if time.helpdesk_ticket_id:
            #         helpdesk_ticket_exists =True
            #         break;
            flag = 0
            for times in rec.timesheet_ids:
                for items in rec.require_items:
                    if times.task_id.id == items.task_id.id:
                        flag = 1
                if flag == 0:
                    rec.timesheet_ids -= times

            for line in rec.require_items:
                # if helpdesk_ticket_exists and line.issue_id.id not in rec.timesheet_ids.product_id.ids:
                #     val={
                #         'helpdesk_ticket_id':rec.id,
                #         'product_id':line.issue_id.id
                #     }
                #     self.env['account.analytic.line'].create(val)
                # else:
                # rec.timesheet_ids=[(5,0,0)]

                if line.task_id and line.task_id.id not in rec.timesheet_ids.task_id.ids:
                    val = [(0, 0, {
                        'product_id': line.issue_id.id,
                        'task_id': line.task_id.id,
                        'project_id': line.project.id,
                        'name': rec.sequence_no + " - " + rec.name,
                        'employee_id': self.env['hr.employee'].search([('user_id', '=', rec.user_id.id)], limit=1).id
                    })]
                    rec.timesheet_ids = val

    # def get_domain(self):
    #     products=self.env['pro']

    # def ticket_close(self):
    #     for rec in self:
    #         rec.job_closing_date = datetime.today()

    sequence_no = fields.Char(default='/')

    def _get_display_name_tree(self):
        display_name = ''
        if self.name:
            display_name = self.name[:70]
        self.dis_name = display_name


    @api.model
    def create(self, vals_list):
        # Create the record first
        res = super(HelpdeskExtend, self).create(vals_list)
        res._get_display_name_tree()
        # Get and set sequence number
        sequence = self.env['ir.sequence'].next_by_sequence_for('helpdesk_ticket')
        if not sequence:
            raise ValidationError(_("Sequence is not configured for helpdesk tickets"))
        res.sequence_no = sequence

        # Prepare description for analytic line
        description = f'{res.sequence_no} - {res.name}'

        # Ensure required fields are available before creating analytic line
        if res.project_id and res.project_id.analytic_account_id:
            self.env['account.analytic.line'].sudo().create({
                'name': description,
                'account_id': res.project_id.analytic_account_id.id,
                'amount': 0,
                'company_id': res.company_id.id if res.company_id else self.env.company.id,
                'date': fields.Date.today(),
                'helpdesk_ticket_id': res.id,
                'employee_id': vals_list.get('dev', False),
                'module_id': vals_list.get('module_id', False),
            })

        # Build the detailed description
        seq = res.sequence_no or ''
        project = res.project_id.name if res.project_id else ''
        module = res.module_id.name if res.module_id else ''

        res.description = (f'Ticket No: {seq}\n'
                           f'Project: {project}\n'
                           f'Module Name: {module}\n'
                           f'Git Pull No: \n'
                           f'Functionality Changed / Action Taken: \n')

        return res

    def write(self, vals):
        res = super(HelpdeskExtend, self).write(vals)
        if vals.get('name'):
            self._get_display_name_tree()
        return res

    @api.onchange('team_id')
    def assign_team_assigned_to(self):
        helpdesk_team = self.env['helpdesk.team'].search([('id', '=', self.team_id.id)])
        if helpdesk_team.member_ids:
            self.user_id = helpdesk_team.member_ids[0].id
        else:
            self.user_id = False
        self.project_id = helpdesk_team.project_id.id

    @api.onchange('project_id')
    def set_customer_name(self):
        for rec in self:
            rec.customer_name = rec.project_id.partner_id.id

    @api.onchange('company_id')
    def get_default_user_id(self):
        context = self._context
        uid = context.get('uid')
        self.user_id = uid

    # Create forum Post
    def forum_post_new(self):
        self.ensure_one()
        if not self.team_id.forum_id:
            raise UserError(_('Help Center not active for this team.'))

        if not self.forum_post_id:
            if self.description_lines:
                description = f'{self.description} \n \n'
            else:
                description = f'{self.description} \n \n ---Not Found!'
            for line in self.description_lines:
                sr_no = line.sr_no
                description1 = line.description_line or ' '
                description += f'{sr_no}. {description1} \n'
            forum_post_content = plaintext2html(description) or ''

            self.forum_post_id = self.env['forum.post'].create({
                'name': self.name,
                'forum_id': self.team_id.forum_id.id,
                'content': forum_post_content,
            }).id

            # Log message
            self.message_post(body=_('Ticket has been shared on the %s forum.') % (self.forum_post_id.forum_id.name,))
        return self.forum_post_open()


class TicketRequireItems(models.Model):
    _name = "require.items"

    ticket_id = fields.Many2one("helpdesk.ticket")
    issue_id = fields.Many2one('product.product', string="Item Name", domain="[('type','=','service')]",
                               compute="get_issue_id", readonly=False, store=True)
    issue = fields.Many2one('product.product', related="ticket_id.main_sub_id")
    # com_issue_id=fields.Many2one('product.product', compute="get_issue_id")
    description = fields.Text(string="Task/Issue Description")
    quantity = fields.Float(default=1, string="Quantity")
    amount = fields.Float(string="Unit Amount")
    total_amount = fields.Float(string="Total Amount")
    menu_id = fields.Many2many('ir.ui.menu', string="Form")
    tech_module = fields.Many2many('ir.module.module', string='Module Technical Name', compute="get_tech_module",
                                   readonly=False, store=True)
    require_db = fields.Many2many('db.list', string="Database Name", compute="get_db_name", readonly=False, store=True)
    line_status = fields.Selection(
        [('assign', 'Assigned'), ('pending', 'Pending'), ('in_progress', 'In Progress'), ('done', 'Done'),
         ('hold', 'Hold')], string="Status", default='assign')
    task_id = fields.Many2one('project.task', string="Task/Issue Name", domain="[('id','in',defult_task_id)]")
    project = fields.Many2one('project.project', related="ticket_id.project")
    defult_task_id = fields.Many2many('project.task', compute="get_tasks")

    @api.depends("line_status")
    def get_issue_id(self):
        for rec in self:
            if rec.ticket_id.require_items and len(rec.ticket_id.require_items) == 1:
                rec.issue_id = rec.ticket_id.main_sub_id.id
            elif not rec.ticket_id.require_items:
                rec.issue_id = rec.ticket_id.main_sub_id.id
            else:
                for line in rec.ticket_id.require_items[-2]:
                    rec.issue_id = line.issue_id.id

    @api.depends("line_status")
    def get_tech_module(self):
        for rec in self:
            if rec.ticket_id.require_items and len(rec.ticket_id.require_items) == 1:
                rec.tech_module = None
            elif not rec.ticket_id.require_items:
                rec.tech_module = None
            else:
                for line in rec.ticket_id.require_items[-2]:
                    rec.tech_module = line.tech_module.ids

    @api.depends("line_status")
    def get_db_name(self):
        for rec in self:
            if rec.ticket_id.require_items and len(rec.ticket_id.require_items) == 1:
                rec.require_db = None
            elif not rec.ticket_id.require_items:
                rec.require_db = None
            else:
                for line in rec.ticket_id.require_items[-2]:
                    rec.require_db = line.require_db.ids

    @api.depends('project')
    def get_tasks(self):
        for rec in self:
            rec.defult_task_id = rec.project.task_ids.ids
            # rec.issue_id=rec.ticket_id.main_sub_id

    @api.onchange('quantity', 'amount')
    def set_total(self):
        for rec in self:
            rec.total_amount = rec.quantity * rec.amount

    def _get_line_numbers(self):
        line_num = 1
        if self.ids:
            first_line_rec = self.browse(self.ids[0])

            for line_rec in first_line_rec.ticket_id.require_items:
                line_rec.sr_no = line_num
                line_num += 1

    sr_no = fields.Integer(compute='_get_line_numbers', string='Sr. No.', readonly=False, default=False)


class TicketDb(models.Model):
    _name = "db.list"

    name = fields.Char(string="DB Name")
    # require_item_ids=fields.Many2one("require.items")


class AccountAnalyticLine(models.Model):
    _inherit = "account.analytic.line"

    product_id = fields.Many2one('product.product', string="Item Name", domain="[('type','=','service')]")

    employee_id = fields.Many2one('hr.employee', string='Employee', default=lambda self: self.get_employee())
    tech_module = fields.Many2many('ir.module.module', string='Module Technical Name', )
    plan_time = fields.Float('PT', default=1.00)

    # name=fields.Char(string="Description", default=lambda self:self.get_name())
    # extra_field=fields.Char()

    @api.onchange('product_id')
    def get_employee(self):
        for rec in self:
            rec.employee_id = rec.helpdesk_ticket_id.dev.id


class HelpdeskDescriptionLine(models.Model):
    _name = 'helpdesk.description.line'

    description_id = fields.Many2one('helpdesk.ticket', 'Helpdesk Ticket Description ID')
    description_line = fields.Text('Check List')
    description_line_2 = fields.Text('Note-1')
    description_line_3 = fields.Text('Note-2')
    ticket_subtask_id = fields.Many2one('project.task', 'Ticket Subtask')
    ticket_subtask_no = fields.Integer('Subtask ID')
    is_create_task = fields.Boolean('')
    stage_id = fields.Many2one('helpdesk.description.stage', 'Stage')
    deadline = fields.Date('Deadline', compute='_get_deadline', inverse='_set_deadline', store=True, readonly=False)

    @api.depends('ticket_subtask_id.date_deadline')
    def _get_deadline(self):
        for rec in self:
            if rec.ticket_subtask_id and rec.ticket_subtask_id.date_deadline:
                rec.deadline = rec.ticket_subtask_id.date_deadline

            else:
                rec.deadline = False

    def _set_deadline(self):
        for rec in self:
            if rec.ticket_subtask_id and rec.deadline:
                rec.ticket_subtask_id.date_deadline = rec.deadline

    @api.model
    def create(self, vals):
        res = super(HelpdeskDescriptionLine, self).create(vals)
        created_task = None
        check_task = None
        if res.is_create_task:
            ticket_name = res.description_id.sequence_no
            last_4 = ticket_name[-4:] if ticket_name else ''
            task_name = f'{last_4} ({res.sr_no:02}) - {res.description_line}'
            parent_task_id = res.description_id.task_id
            project_id = parent_task_id.project_id


            if res.ticket_subtask_no:
                check_task = self.env['project.task'].search([
                    ('id', '=', res.ticket_subtask_no)
                ])
            if check_task:
                created_task = check_task
            else:
                created_task = self.create_subtask(task_name, project_id, parent_task_id)
            res.ticket_subtask_id = created_task.id
            res.ticket_subtask_no = created_task.id
            task_created = True
            # res.deadline = created_task.date_deadline if created_task.date_deadline else False
        else:
            res.ticket_subtask_id = False
        # time_sheet_ids
        time_sheet_id = self.env['account.analytic.line'].search([
            ('name', '=', res.description_line)
        ], limit=1)
        if time_sheet_id:
            time_sheet_id.write({
                'helpdesk_ticket_id': res.description_id.id
            })
        if not time_sheet_id:
            time_sheet_id = self.env['account.analytic.line'].create({
                'helpdesk_ticket_id': res.description_id.id,
                'name': res.description_line,
                'date': res.deadline if res.deadline else date.today(),
                'task_id': res.description_id.task_id.id,
                'sub_task': created_task.id if created_task else False,
                'employee_id': res.description_id.dev.id if res.description_id.dev else self.env.user.employee_id.id,
            })
            print(time_sheet_id)
        return res

    def write(self, vals):
        if 'is_create_task' in vals and vals.get('is_create_task') == True and not self.ticket_subtask_id:
            ticket_name = self.description_id.sequence_no
            last_4 = ticket_name[-4:] if ticket_name else ''
            task_name = f'{last_4} ({self.sr_no:02}) - {self.description_line}'
            parent_task_id = self.description_id.task_id
            project_id = parent_task_id.project_id
            created_task = None
            check_task = None
            if self.ticket_subtask_no:
                check_task = self.env['project.task'].search([
                    ('id', '=', self.ticket_subtask_no)
                ])
            if check_task:
                created_task = check_task
            else:
                created_task = self.create_subtask(task_name, project_id, parent_task_id)
            self.ticket_subtask_id = created_task.id
            self.ticket_subtask_no = created_task.id
            print(self.ticket_subtask_no)
        elif 'is_create_task' in vals and vals.get('is_create_task') == False and self.ticket_subtask_id:
                self.ticket_subtask_id = False

        if 'description_line' in vals and self.ticket_subtask_no:
            ticket_name = self.description_id.sequence_no
            last_4 = ticket_name[-4:] if ticket_name else ''
            description_line = vals.get('description_line', '')
            task_name = f'{last_4} ({self.sr_no:02}) - {description_line}'
            task = self.env['project.task'].search([
                ('id', '=', self.ticket_subtask_no)
            ], limit=1)
            if task:
                task.write({
                    'name': task_name
                })

        # else:
        #     self.ticket_subtask_id = False

        return super(HelpdeskDescriptionLine, self).write(vals)

    def create_subtask(self, task_name, project_id, parent_task_id):
        created_subtask = self.env['project.task'].create({
            'name': task_name,
            'project_id': project_id.id,
            'parent_id': parent_task_id.id,
        })
        return created_subtask

    def _get_line_numbers(self):
        line_num = 1
        if self.ids:
            first_line_rec = self.browse(self.ids[0])

            for line_rec in first_line_rec.description_id.description_lines:
                line_rec.sr_no = line_num
                line_num += 1

    sr_no = fields.Integer(compute='_get_line_numbers', string='Sr. No.', readonly=False, default=False)


class IrModuleInherit(models.Model):
    _inherit = 'ir.module.module'

    def name_get(self):
        result = []

        if self.env.context.get('custom_search', True):
            for record in self:
                # Only goes off when the custom_search is in the context values.
                result.append((record.id, record.name))
            return result
        else:
            return super(IrModuleInherit, self).name_get()


class HelpdeskDescriptionStage(models.Model):
    _name = 'helpdesk.description.stage'
    _description = 'Helpdesk Description stage'

    name = fields.Char('Name')