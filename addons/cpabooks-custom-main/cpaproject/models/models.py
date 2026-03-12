# -*- coding: utf-8 -*-

from odoo import fields, models, _, api


class ProjectProjectInherit(models.Model):
    _inherit = "project.project"

    project_import_or_export = fields.Selection([('export', 'Export'),('import', 'Import')], string='Exp/Imp', required=True)
    project_sl_no = fields.Char(string='Serial  No', required=True, copy=False, readonly=True,
                                 index=True, default=lambda self: _('New'))
    project_month = fields.Selection([('january', 'January'), ('february', 'February'), ('march', 'March'), ('april', 'April'),
                              ('may', 'May'), ('june', 'June'), ('july', 'July'), ('august', 'August'),
                              ('september', 'September'), ('october', 'October'), ('november', 'November'), ('december', 'December')],
                             string='Month')
    project_bill_of_ladding = fields.Char("Bill of Ladding")
    project_container_no = fields.Char("Container No.")
    project_booking_no = fields.Char("Booking No.")
    project_ref = fields.Char("Reference No.")
    project_etd = fields.Date("ETD")
    port_of_loading = fields.Many2one('cpaproject.port_of_loading', string="POL")
    project_sales_person = fields.Many2one('res.users', string='Salesperson', default=lambda self: self.env.user, tracking=True)
    # project_sales_person = fields.Many2one('res.users', string='Salesperson', store=True, readonly=True)
    project_vassel_name = fields.Char("Vassel Name")
    project_port_of_destination = fields.Char("POD")
    project_service = fields.Char("Service")
    project_ts = fields.Char("T/S")
    # project_status = fields.Selection([('pending', 'Pending'), ('cancelled', 'Cancelled'), ('booked', 'Booked'), ('sailed', 'Sailed')], string='Status', default='pending')
    project_status01 = fields.Many2one('cpaproject.status', string='Status')
    project_dostatus = fields.Many2one('cpaproject.dostatus', string='DO Status')

    project_item_qty = fields.Integer("Volume (Qty)")
    project_container_type = fields.Selection([('20', '20 STD'), ('40', '40 STD'), ('41', '40 HC'), ('45', '45 HC')], string='Container Type', default='20')
    project_teus20ft = fields.Float(string="TEUS (20ft)")
    project_ffe40ft = fields.Float(string="FFE (40ft)")
    project_est_cost = fields.Integer(string="Est. Cost")
    project_est_sales = fields.Integer(string="Est. Sales")

    project_validity = fields.Date("Validity")
    project_carier = fields.Char("Carier")
    project_billofentry = fields.Many2one('cpaproject.billofentry', string='BOE')

    project_si_submitted = fields.Selection([('yes', 'Yes'),('no', 'No'), ('cancelled', 'Cancelled'), ('done', 'Done')], string='SI Submitted', default='yes')
    project_vgm = fields.Selection([('yes', 'Yes'),('no', 'No'), ('cancelled', 'Cancelled')], string='VGM', default='yes')
    project_bl_draft = fields.Selection([('yes', 'Yes'),('no', 'No'), ('sent_to_customer', 'Sent to Customer'), ('approved', 'Approved'), ('cancelled', 'Cancelled')], string='BL Draft', default='yes')
    project_swb = fields.Selection([('yes', 'Yes'),('no', 'No'), ('cancelled', 'Cancelled')], string='SWB', default='yes')
    project_invoice = fields.Selection([('yes', 'Yes'),('no', 'No'), ('cancelled', 'Cancelled')], string='Invoice', default='yes')
    project_job = fields.Char("Job")
    project_eta = fields.Date("ETA")
    project_destination = fields.Char("Destination")
    project_remarks = fields.Selection([('pending', 'Pending'), ('approved', 'Approved'), ('completed', 'Completed'), ('sent_to_customer', 'Sent to Customer'), ('sent_to_carrier', 'Sent to Carrier')], string='Remarks', default='pending')
    project_paying = fields.Char("Paying")
    project_selling = fields.Char("Selling")


    @api.onchange('project_item_qty', 'project_container_type')
    def _compute_sum(self):
        for rec in self:
            rec.project_teus20ft = (rec.project_item_qty * int(rec.project_container_type)) / 20
            rec.project_ffe40ft = (rec.project_item_qty * int(rec.project_container_type)) / 40


    @api.model
    def create(self, vals):
        if vals.get('project_sl_no', _('New')) == _('New'):
            vals['project_sl_no'] = self.env['ir.sequence'].next_by_code(
                'project.project') or _('New')
        res = super(ProjectProjectInherit, self).create(vals)
        return res


class PortofLoading(models.Model):
    _name="cpaproject.port_of_loading"
    _description= "Port of Loading"
    name=fields.Char(string="POL")


class ProjectStatus(models.Model):
    _name="cpaproject.status"
    _description= "Status"
    name=fields.Char(string="Status")

class ProjectDostatus(models.Model):
    _name="cpaproject.dostatus"
    _description= "Status"
    name=fields.Char(string="DO Status")

class ProjectBillofentry(models.Model):
    _name="cpaproject.billofentry"
    _description= "Status"
    name=fields.Char(string="BOE")
