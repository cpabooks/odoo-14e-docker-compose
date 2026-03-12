from odoo import models, fields, api


class TimesheetAdd(models.Model):
    _name = 'timesheet.template.apply'

    name=fields.Char()
    template_id=fields.Many2one('timesheet.template.config', string="Template" , domain="[('is_active','=',True),('company_id','=',company_id)]")
    apply_date=fields.Date(string="Timesheet Date",required=True)
    project_id=fields.Many2one(string="Project",related="template_id.project_id")
    task_id=fields.Many2one(string="Tasks",related="template_id.task_id")
    company_id = fields.Many2one('res.company', string="Company", required=True,
                                 default=lambda self: self.env.company.id)
    state=fields.Selection([('draft','Draft'),('added','Added into timesheet')], default="draft",readonly=True)
    
    timesheet_apply_line=fields.One2many('timesheet.template.apply.line','timesheet_apply_id',string="Timesheet Apply Line")

    @api.onchange('template_id')
    def assign_line_data(self):
        val_list=[]
        for rec in self.template_id.timesheet_line:
            vals=(0,0,{
                'employee_id':rec.employee_id,
                'description':rec.description,
                'unit_amount':rec.unit_amount,
                'task':rec.task.id
            })
            val_list.append(vals)
        self.timesheet_apply_line=val_list

    def add_into_timesheet(self):
        val_list=[]
        for rec in self.timesheet_apply_line:
            vals={
                'name':rec.description,
                'date':rec.timesheet_apply_id.apply_date,
                'unit_amount':rec.unit_amount,
                'account_id':rec.timesheet_apply_id.project_id.analytic_account_id.id,
                'user_id':rec.employee_id.user_id.id,
                'company_id':rec.timesheet_apply_id.company_id.id,
                'currency_id':rec.timesheet_apply_id.company_id.currency_id.id,
                'so_line':rec.timesheet_apply_id.task_id.sale_line_id.id,
                'task_id':rec.task.id,
                'project_id':rec.timesheet_apply_id.project_id.id,
                'employee_id':rec.employee_id.id,
                'department_id':rec.employee_id.department_id.id,
                'validated':False
            }
            val_list.append(vals)
        self.env['account.analytic.line'].sudo().create(val_list)
        self.state='added'


    
class TimesheetAddLine(models.Model):
    _name = 'timesheet.template.apply.line'

    timesheet_apply_id=fields.Many2one('timesheet.template.apply')
    employee_id=fields.Many2one('hr.employee',string="Employee")
    description=fields.Char(string="Description" ,default="Timesheet Adjustment")
    unit_amount=fields.Float(string="Duration")
    project = fields.Many2one('project.project', related="timesheet_apply_id.project_id")
    task=fields.Many2one('project.task',string="Task", domain="[('project_id','=',project)]")
