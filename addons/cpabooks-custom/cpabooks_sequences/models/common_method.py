import re

from odoo import models, fields, api,_
from odoo.exceptions import ValidationError

class CommonMetthod(models.AbstractModel):
    _name = "common.method"

    def get_highest_seq_for_year_yearly(self,get_sequence_object,date_obj,model,extra_condition=False):
        padding = get_sequence_object.padding
        actual_prefix = get_sequence_object.prefix.split('%')
        prefix = f'{actual_prefix[0]}{date_obj.year}'
        pattern = re.compile(
            rf'^{re.escape(prefix)}/\d{{{int(padding)}}}$')
        if extra_condition:
            orders = self.env[model].sudo().search([
                ('name', 'like', prefix),
                ('id', '!=', self.id),('company_id','=',self.env.company.id),extra_condition
            ])
        else:
            orders = self.env[model].sudo().search([
                ('name', 'like', prefix),
                ('id', '!=', self.id),('company_id','=',self.env.company.id)
            ])
        # Filter to only those that match the exact structure
        valid_orders = [o for o in orders if pattern.match(o.name)]
        # Sort and get the one with the highest number
        highest_order = None
        if valid_orders:
            highest_order = max(valid_orders, key=lambda o: int(o.name.split('/')[-1]))
        get_highest_sequence = highest_order if highest_order else None
        return get_highest_sequence

    def get_highest_seq_for_month_year_monthly(self,get_sequence_object,date_obj,model,extra_condition=False):
        padding = get_sequence_object.padding
        actual_prefix = get_sequence_object.prefix.split('%')
        month = str(date_obj.strftime('%m'))
        prefix = f'{actual_prefix[0]}{date_obj.year}/{month}'
        pattern = re.compile(
            rf'^{re.escape(prefix)}/\d{{{int(padding)}}}$')
        if extra_condition:
            orders = self.env[model].sudo().search([
                ('name', 'like', prefix),
                ('id', '!=', self.id),('company_id','=',self.env.company.id),extra_condition
            ])
        else:
            orders = self.env[model].sudo().search([
                ('name', 'like', prefix),
                ('id', '!=', self.id),('company_id','=',self.env.company.id)
            ])
        # Filter to only those that match the exact structure
        valid_orders = [o for o in orders if pattern.match(o.name)]
        # Sort and get the one with the highest number
        highest_order = None
        if valid_orders:
            highest_order = max(valid_orders, key=lambda o: int(o.name.split('/')[-1]))
        get_highest_sequence = highest_order if highest_order else None
        return get_highest_sequence

    def get_highest_seq_no(self, get_sequence_object, date_obj, model):
        padding = get_sequence_object.padding
        actual_prefix = get_sequence_object.prefix.split('%')
        prefix = f'{actual_prefix[0]}{date_obj.year}/'
        pattern = re.compile(
            rf'^{re.escape(prefix)}\d{{{int(padding)}}}$')

        get_highest_sequence = self.env[model].sudo().search([
            ('sequence_prefix', '=', prefix),
            ('id', '!=', self.id),('company_id','=',self.env.company.id)
        ],limit=1,order="sequence_number desc").sequence_number

        return get_highest_sequence

    def get_highest_seq_no_month_year_monthly(self, get_sequence_object, date_obj, model):
        padding = get_sequence_object.padding
        actual_prefix = get_sequence_object.prefix.split('%')
        month = str(date_obj.strftime('%m'))
        prefix = f'{actual_prefix[0]}{date_obj.year}/{month}/'
        pattern = re.compile(
            rf'^{re.escape(prefix)}\d{{{int(padding)}}}$')

        get_highest_sequence_a = self.env[model].sudo().search([
            ('sequence_prefix', '=', prefix),
            ('id', '!=', self.id),('company_id','=',self.env.company.id)
        ], limit=1, order="sequence_number desc")
        get_highest_sequence = self.env[model].sudo().search([
            ('sequence_prefix', '=', prefix),
            ('id', '!=', self.id),('company_id','=',self.env.company.id)
        ], limit=1, order="sequence_number desc").sequence_number

        return get_highest_sequence