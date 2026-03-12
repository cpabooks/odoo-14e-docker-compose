# -*- coding: utf-8 -*-
from odoo import api, fields, models

class CRMGCL(models.Model):
    _name = "crm.gcl"
    _description = "CRM GCL"

    building = fields.Text(string='Building', required=True)
    flat = fields.Text(string='Flat')
    problem_type = fields.Text(string='Problem Type')
    problem = fields.Text(string='problem')
    problem_category = fields.Text(string='Problem Category')
    tenant = fields.Text(string='Tenant')
    mobile = fields.Text(string='Mobile Number')
    email = fields.Text(string='Email Address')
    priority = fields.Text(string='Priority')
    address = fields.Text(string='Address')
    option = fields.Text(string='Option')