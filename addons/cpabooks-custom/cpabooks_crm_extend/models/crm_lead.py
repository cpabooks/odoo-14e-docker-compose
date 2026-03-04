# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta
from decimal import Decimal



class CrmLead(models.Model):
    _inherit = 'crm.lead'

    system_admin = fields.Boolean(compute="_get_system_admin")
    enquiry_number = fields.Char(string='Enquiry Number', required=True, copy=False, readonly=True, index=True, default=lambda self: _('New'))
    customer_ref=fields.Char(string="Customer Ref.")
    consultant_company_name=fields.Many2one('res.partner')
    consultant_street=fields.Char(string="Street")
    consultant_street2=fields.Char(string="Street2")
    consultant_city=fields.Char(string="City")
    consultant_state_id=fields.Many2one('res.country.state',string="State")
    consultant_zip=fields.Char(string="Zip")
    consultant_country_id=fields.Many2one('res.country',string="Country")
    consultant_website=fields.Char(string="Website")
    consultant_lang_id=fields.Many2one('res.lang',string="Language")

    client_company_name = fields.Many2one('res.partner')
    client_street = fields.Char(string="Street")
    client_street2 = fields.Char(string="Street2")
    client_city = fields.Char(string="City")
    client_state_id = fields.Many2one('res.country.state', string="State")
    client_zip = fields.Char(string="Zip")
    client_country_id = fields.Many2one('res.country', string="Country")
    client_website = fields.Char(string="Website")
    client_lang_id = fields.Many2one('res.lang', string="Language")

    project_id=fields.Many2one('project.project',string="project")
    crm_date=fields.Date(string="CRM Create Date",default=datetime.today())
    next_action = fields.Char('Next Action', size=100, tracking=True)
    next_action_date = fields.Date('Next Action Date', tracking=True)
    last_action = fields.Char('Last Action', size=100, tracking=True)
    summary_note = fields.Text('Summary Note', tracking=True)

    @api.model
    def default_get(self, fields_list):
        res = super(CrmLead, self).default_get(fields_list)
        today_plus_7 = datetime.today() + timedelta(days=7)
        res.update({
            'next_action_date': today_plus_7,
            'bypass_estimation': True
        })
        return res

    @api.onchange('consultant_company_name')
    def set_details(self):
        for rec in self:
            rec.consultant_street=rec.consultant_company_name.street
            rec.consultant_street2=rec.consultant_company_name.street2
            rec.consultant_city=rec.consultant_company_name.city
            rec.consultant_state_id=rec.consultant_company_name.state_id.id
            rec.consultant_zip=rec.consultant_company_name.zip
            rec.consultant_country_id=rec.consultant_company_name.country_id.id
            rec.consultant_website=rec.consultant_company_name.website
            # res=self.env['res.lang'].get_installed()
            # res1=self.env['res.lang'].sudo().search([('name','=',res)])
            rec.consultant_lang_id=self.env['res.lang'].sudo().search([('code','=',rec.consultant_company_name.lang)]).id

    @api.onchange('client_company_name')
    def set_client_details(self):
        for rec in self:
            rec.client_street = rec.client_company_name.street
            rec.client_street2 = rec.client_company_name.street2
            rec.client_city = rec.client_company_name.city
            rec.client_state_id = rec.client_company_name.state_id.id
            rec.client_zip = rec.client_company_name.zip
            rec.client_country_id = rec.client_company_name.country_id.id
            rec.client_website = rec.client_company_name.website
            # res=self.env['res.lang'].get_installed()
            # res1=self.env['res.lang'].sudo().search([('name','=',res)])
            rec.client_lang_id = self.env['res.lang'].sudo().search(
                [('code', '=', rec.client_company_name.lang)]).id

    @api.depends('stage_id')
    def _get_system_admin(self):
        for rec in self:
            get_admin_power_group = self.env['res.groups'].sudo().search([('name', '=ilike', 'Admin Power')])
            if get_admin_power_group:
                if self.env.user.has_group('base.group_system') or self.env.user.id in get_admin_power_group.users.ids:
                    rec.system_admin = True
                else:
                    rec.system_admin = False
            else:
                if self.env.user.has_group('base.group_system'):
                    rec.system_admin = True
                else:
                    rec.system_admin = False

    @api.model
    def create(self, vals):
        if not vals.get('enquiry_number') or vals['enquiry_number'] == _('New'):
            vals['enquiry_number'] = self.env['ir.sequence'].next_by_code('crm.lead') or _('New')
        res=super(CrmLead, self).create(vals)
        # res = super(CrmLead, self).create(vals)
        # get_sequence = self.env['ir.sequence'].next_by_sequence_for('crm')
        # if not get_sequence:
        #     raise ValidationError(_("Sequence is not set for CRM"))
        # res.enquiry_number = get_sequence or _('/')
        # return res
        company_id = self.env.company.id
        get_sequence_object = self.env['ir.sequence'].sudo().search(
            [('sequence_for', '=', 'crm'), ('company_id', 'in', [company_id, False])],
            limit=1, )
        if res.enquiry_number != '/' or res.enquiry_number.upper() != 'DRAFT' or res.enquiry_number.upper() != 'NEW':
            crm_name = ''
        if res.enquiry_number == '/' or res.enquiry_number.upper() == 'DRAFT' or res.enquiry_number.upper() == 'NEW':
            crm_name = ''
        get_sequence = self.env['ir.sequence'].next_by_sequence_for('crm')
        if get_sequence:
            get_highest_crm = self.env['crm.lead'].sudo().search(
                [('id', '!=', self.id)], limit=1, order='id desc')
            get_sequence = res._get_sequence(get_sequence_object, get_sequence, vals, get_highest_crm, crm_name)

        if not get_sequence:
            raise ValidationError(_("Sequence is not set for CRM lead"))
        res.enquiry_number = get_sequence or _('/')
        return res

    def _get_sequence(self, get_sequence_object, get_sequence, vals_list, get_highest_crm, crm_name):
        if '/%(year)s/%(month)s/' in get_sequence_object.prefix and get_sequence_object.sequence_pattern == 'month_year':
            if crm_name != '':
                split_crm_name = crm_name.split('/')
                split_seq = get_sequence.split('/')
                split_crm_name_last_value = split_crm_name[-1]
                split_seq[-1] = split_crm_name_last_value
                if get_highest_crm and get_highest_crm.enquiry_number != '/':
                    split_highest_inv = get_highest_crm.enquiry_number.split('/')
                    # get_sequence_object.number_next_actual=int(split_highest_inv[-1])+1
                    get_sequence_object.number_next_actual = get_sequence_object.number_next_actual - 1
            else:
                split_seq = get_sequence.split('/')
                # split_highest_inv = get_highest_crm.split('/')
                # get_sequence_object.number_next_actual = int(split_highest_inv[-1]) + 1
            # if 'date_order' in vals_list.keys() and not isinstance(vals_list['date_order'],
            #                                                        bool):
            #     if get_sequence.find(str(datetime.now().year)) > -1:
            #         idx = split_seq.index(str(datetime.now().year))
            #         split_seq[idx] = str(vals_list['date_order']).split('-')[0]
            #         get_sequence = "/".join(split_seq)
            #     if get_sequence.find(str(datetime.now().month)) > -1:
            #         # if not get_sequence.find(str(vals_list['invoice_date']).split('-')[1]) > -1:
            #         month = datetime.now().month
            #         str_month = str(datetime.now().month)
            #         if month < 10:
            #             str_month = str(0) + str_month
            #         idx = split_seq.index(str_month)
            #         split_seq[idx] = str(vals_list['date_order']).split('-')[1]
            #         get_sequence = "/".join(split_seq)
            # if 'date_order' not in vals_list.keys() and not isinstance(self.date_order,
            #                                                            bool):
            if get_sequence.find(str(datetime.now().year)) > -1:
                idx = split_seq.index(str(datetime.now().year))
                split_seq[idx] = str(datetime.now()).split('-')[0]
                get_sequence = "/".join(split_seq)
            if get_sequence.find(str(datetime.now().month)) > -1:
                # if not get_sequence.find(str(vals_list['invoice_date']).split('-')[1]) > -1:
                month = datetime.now().month
                str_month = str(datetime.now().month)
                if month < 10:
                    str_month = str(0) + str_month
                idx = split_seq.index(str_month)
                split_seq[idx] = str(datetime.now()).split('-')[1]
                get_sequence = "/".join(split_seq)
            return get_sequence

        elif '/%(year)s/%(month)s/' in get_sequence_object.prefix and get_sequence_object.sequence_pattern == 'month_year_monthly':
            if get_sequence != '':
                split_inv_name = get_sequence.split('/')
                split_seq = get_sequence.split('/')
                split_inv_name_last_value = split_inv_name[-1]
                split_seq[-1] = split_inv_name_last_value
                if get_highest_crm and get_highest_crm.enquiry_number != '/':
                    split_highest_inv = get_highest_crm.enquiry_number.split('/')
                    # get_sequence_object.number_next_actual=int(split_highest_inv[-1])+1
                    get_sequence_object.number_next_actual = get_sequence_object.number_next_actual - 1
            else:
                split_seq = get_sequence.split('/')
                get_sequence_object.number_next_actual = get_sequence_object.number_next_actual - 1
                # split_highest_inv = get_highest_inv.split('/')
                # get_sequence_object.number_next_actual = int(split_highest_inv[-1]) + 1
            # if 'date_order' in vals_list.keys() and not isinstance(vals_list['date_order'],
            #                                                        bool):
            if get_sequence.find(str(datetime.now().year)) > -1:
                idx = split_seq.index(str(datetime.now().year))
                split_seq[idx] = str(datetime.now()).split('-')[0]
                get_sequence = "/".join(split_seq)
            if get_sequence.find(str(datetime.now().month)) > -1:
                # if not get_sequence.find(str(vals_list['invoice_date']).split('-')[1]) > -1:
                month = datetime.now().month
                str_month = str(datetime.now().month)
                if month < 10:
                    str_month = str(0) + str_month
                idx = split_seq.index(str_month)
                split_seq[idx] = str(datetime.now()).split('-')[1]
                get_sequence = "/".join(split_seq)

                # region Month wise sequence
                orginal_sequence = get_sequence.split('/')
                split_sequence_prefix = get_sequence.split('/')
                without_last_index = split_sequence_prefix.pop()
                without_last_index_sequence = "/".join(split_sequence_prefix)
                without_last_index_sequence += "/"
                get_highest_sequence = self.env['crm.lead'].search(
                    [('enquiry_number', 'like', without_last_index_sequence),
                     ('id', '!=', self.id)],
                    order="enquiry_number desc",
                    limit=1)
                sequence_padding = get_sequence_object.padding
                get_highest_sequence_no = 0
                if get_highest_sequence:
                    highest_seq = get_highest_sequence.enquiry_number.split('/')
                    get_highest_sequence_no = int(highest_seq[-1])
                if len(str(get_highest_sequence_no)) > sequence_padding:
                    number = get_highest_sequence_no + 1
                    string_convert = str(number)
                    orginal_sequence[-1] = string_convert
                else:
                    common = '1'
                    divide_by = int(common.ljust(sequence_padding + 1, '0'))
                    number = (get_highest_sequence_no + 1) / divide_by
                    dec_string = str(round(Decimal(number), sequence_padding))
                    string_convert = dec_string.split('.')[1]
                    orginal_sequence[-1] = string_convert

                get_sequence = "/".join(orginal_sequence)

            return get_sequence

        elif '/%(year)s/%(month)s/' not in get_sequence_object.prefix and '/%(year)s/' in get_sequence_object.prefix and get_sequence_object.sequence_pattern == 'year':
            if crm_name != '':
                split_inv_name = crm_name.split('/')
                split_seq = get_sequence.split('/')
                split_inv_name_last_value = split_inv_name[-1]
                split_seq[-1] = split_inv_name_last_value
                if get_highest_crm and get_highest_crm.enquiry_number != '/':
                    split_highest_inv = get_highest_crm.enquiry_number.split('/')
                    # get_sequence_object.number_next_actual=int(split_highest_inv[-1])+1
                    get_sequence_object.number_next_actual = get_sequence_object.number_next_actual - 1
            else:
                split_seq = get_sequence.split('/')
            # if 'date_order' in vals_list.keys() and not isinstance(vals_list['date_order'],
            #                                                        bool):
            if get_sequence.find(str(datetime.now().year)) > -1:
                idx = split_seq.index(str(datetime.now().year))
                split_seq[idx] = str(datetime.now()).split('-')[0]
                get_sequence = "/".join(split_seq)

            # if 'date_order' not in vals_list.keys() and not isinstance(self.date_order,
            #                                                            bool):
            #     if get_sequence.find(str(datetime.now().year)) > -1:
            #         idx = split_seq.index(str(datetime.now().year))
            #         split_seq[idx] = str(self.date_order).split('-')[0]
            #         get_sequence = "/".join(split_seq)

            return get_sequence

        elif '/%(year)s/%(month)s/' not in get_sequence_object.prefix and '/%(year)s/' in get_sequence_object.prefix and get_sequence_object.sequence_pattern == 'year_yearly':
            if crm_name != '':
                split_inv_name = crm_name.split('/')
                split_seq = get_sequence.split('/')
                split_inv_name_last_value = split_inv_name[-1]
                split_seq[-1] = split_inv_name_last_value
                if get_highest_crm and get_highest_crm.enquiry_number != '/':
                    split_highest_inv = get_highest_crm.enquiry_number.split('/')
                    # get_sequence_object.number_next_actual = int(split_highest_inv[-1]) + 1
                    get_sequence_object.number_next_actual = get_sequence_object.number_next_actual - 1
            else:
                split_seq = get_sequence.split('/')
                get_sequence_object.number_next_actual = get_sequence_object.number_next_actual - 1
            # if 'date_order' in vals_list.keys() and not isinstance(vals_list['date_order'],
            #                                                        bool):
            if get_sequence.find(str(datetime.now().year)) > -1:
                idx = split_seq.index(str(datetime.now().year))
                split_seq[idx] = str(datetime.now()).split('-')[0]
                get_sequence = "/".join(split_seq)

                # region year wise sequence
                orginal_sequence = get_sequence.split('/')
                split_sequence_prefix = get_sequence.split('/')
                without_last_index = split_sequence_prefix.pop()
                without_last_index_sequence = "/".join(split_sequence_prefix)
                without_last_index_sequence += "/"
                get_highest_sequence = self.env['crm.lead'].search(
                    [('enquiry_number', 'like', without_last_index_sequence),
                     ('id', '!=', self.id)],
                    order="enquiry_number desc",
                    limit=1)
                sequence_padding = get_sequence_object.padding
                get_highest_sequence_no = 0
                if get_highest_sequence:
                    highest_seq = get_highest_sequence.enquiry_number.split('/')
                    get_highest_sequence_no = int(highest_seq[-1])
                if len(str(get_highest_sequence_no)) > sequence_padding:
                    number = get_highest_sequence_no + 1
                    string_convert = str(number)
                    orginal_sequence[-1] = string_convert
                else:
                    common = '1'
                    divide_by = int(common.ljust(sequence_padding + 1, '0'))
                    number = (get_highest_sequence_no + 1) / divide_by
                    dec_string = str(round(Decimal(number), sequence_padding))
                    string_convert = dec_string.split('.')[1]
                    orginal_sequence[-1] = string_convert

                get_sequence = "/".join(orginal_sequence)
                # endregion



            return get_sequence

        elif '/%(year)s/%(month)s/' not in get_sequence_object.prefix and '/%(month)s/' in get_sequence_object.prefix:
            if crm_name != '':
                split_inv_name = crm_name.split('/')
                split_seq = get_sequence.split('/')
                split_inv_name_last_value = split_inv_name[-1]
                split_seq[-1] = split_inv_name_last_value
                if get_highest_crm and get_highest_crm.enquiry_number != '/':
                    split_highest_inv = get_highest_crm.enquiry_number.split('/')
                    get_sequence_object.number_next_actual = int(split_highest_inv[-1]) + 1
            else:
                split_seq = get_sequence.split('/')
           
            if get_sequence.find(str(datetime.now().month)) > -1:
                # if not get_sequence.find(str(vals_list['invoice_date']).split('-')[1]) > -1:
                month = datetime.now().month
                str_month = str(datetime.now().month)
                if month < 10:
                    str_month = str(0) + str_month
                idx = split_seq.index(str_month)
                split_seq[idx] = str(datetime.now()).split('-')[1]
                get_sequence = "/".join(split_seq)
           
            return get_sequence


        else:
            if crm_name != '':
                split_inv_name = crm_name.split('/')
                split_seq = get_sequence.split('/')
                split_inv_name_last_value = split_inv_name[-1]
                split_seq[-1] = split_inv_name_last_value
                get_sequence = "/".join(split_seq)
                if get_highest_crm and get_highest_crm.enquiry_number != '/':
                    split_highest_inv = get_highest_crm.enquiry_number.split('/')
                    # get_sequence_object.number_next_actual = int(split_highest_inv[-1]) + 1
                    get_sequence_object.number_next_actual = get_sequence_object.number_next_actual - 1
            else:
                split_seq = get_sequence.split('/')
                get_sequence = "/".join(split_seq)
            return get_sequence

    def action_new_quotation(self):
        action = super().action_new_quotation()
        action['context']['default_enquiry_number'] = self.enquiry_number
        return action
