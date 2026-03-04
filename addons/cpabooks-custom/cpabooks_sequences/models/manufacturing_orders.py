from decimal import Decimal

from odoo import models, fields, api,_
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta


class ManufacturingOrderInheritance(models.Model):
    _inherit = 'mrp.production'

    system_admin = fields.Boolean(compute="_get_system_admin")

    # @api.depends('state')
    # def _get_system_admin(self):
    #     for rec in self:
    #         get_admin_power_group = self.env['res.groups'].sudo().search([('name', '=ilike', 'Sequence Editor')])
    #         if get_admin_power_group:
    #             if self.env.user.has_group('base.group_system') or self.env.user.id in get_admin_power_group.users.ids:
    #                 rec.system_admin = True
    #             else:
    #                 rec.system_admin = False
    #         else:
    #             if self.env.user.has_group('base.group_system'):
    #                 rec.system_admin = True
    #             else:
    #                 rec.system_admin = False
    @api.depends('state')
    def _get_system_admin(self):
        for rec in self:
            rec.system_admin = False
            get_admin_power_group = self.env['res.groups'].sudo().search([('name', '=ilike', 'Sequence Editor')])
            if get_admin_power_group:
                if self.env.user.id in get_admin_power_group.users.ids:
                    rec.system_admin = True
                else:
                    rec.system_admin = False
            # else:
            #     if self.env.user.has_group('base.group_system'):
            #         rec.system_admin = True
            #     else:
            #         rec.system_admin = False

    @api.model
    def create(self, vals_list):
        print(vals_list)
        # if 'name' in vals_list.keys():
        vals_list['name']='/'
        res = super(ManufacturingOrderInheritance, self).create(vals_list)
        # get_sequence = self.env['ir.sequence'].next_by_sequence_for('manufacturing')
        # actual_sequence=res.name.split("/")[-1]
        # made_up_sequence=get_sequence.split("/")
        # made_up_sequence[-1]=actual_sequence
        # get_sequence = "/".join(made_up_sequence)
        # get_sequence_settings=self.env['ir.sequence'].sudo().search([('sequence_for','=','manufacturing')],limit=1)
        # if get_sequence_settings:
        #     get_sequence_settings.number_next_actual=int(actual_sequence)+1

        company_id = self.env.company.id
        get_sequence_object = self.env['ir.sequence'].sudo().search(
            [('sequence_for', '=', 'manufacturing'), ('company_id', 'in', [company_id, False])],
            limit=1, )
        if res.name != '/' or res.name.upper() != 'DRAFT' or res.name.upper() != 'NEW':
            manufacture_name = ''
        if res.name == '/' or res.name.upper() == 'DRAFT' or res.name.upper() == 'NEW':
            manufacture_name = ''
        get_sequence = self.env['ir.sequence'].next_by_sequence_for('manufacturing')
        if get_sequence:
            get_highest_manufacture = self.env['mrp.production'].sudo().search(
                [('id', '!=', res.id)], limit=1, order='id desc')
            get_sequence = res._get_sequence(get_sequence_object, get_sequence, vals_list, get_highest_manufacture, manufacture_name)
        if not get_sequence:
            raise ValidationError(_("Sequence is not set for Manufacturing Orders"))
        res.name = get_sequence or _('/')
        return res

    def _get_sequence(self, get_sequence_object, get_sequence, vals_list, get_highest_manufacture, manufacture_name):
        common_method = self.env['common.method']
        model = 'mrp.production'
        if '/%(year)s/%(month)s/' in get_sequence_object.prefix and get_sequence_object.sequence_pattern == 'month_year':
            if manufacture_name != '':
                split_manufacture_name = manufacture_name.split('/')
                split_seq = get_sequence.split('/')
                split_manufacture_name_last_value = split_manufacture_name[-1]
                split_seq[-1] = split_manufacture_name_last_value
                if get_highest_manufacture and get_highest_manufacture.name != '/':
                    split_highest_inv = get_highest_manufacture.name.split('/')
                    # get_sequence_object.number_next_actual=int(split_highest_inv[-1])+1
                    get_sequence_object.number_next_actual = get_sequence_object.number_next_actual - 1
            else:
                split_seq = get_sequence.split('/')
                # split_highest_inv = get_highest_manufacture.split('/')
                # get_sequence_object.number_next_actual = int(split_highest_inv[-1]) + 1
            if 'date_planned_start' in vals_list.keys() and not isinstance(vals_list['date_planned_start'],
                                                                   bool):
                if get_sequence.find(str(datetime.now().year)) > -1:
                    idx = split_seq.index(str(datetime.now().year))
                    split_seq[idx] = str(vals_list['date_planned_start']).split('-')[0]
                    get_sequence = "/".join(split_seq)


                if get_sequence.find(str(datetime.now().month)) > -1:
                    # if not get_sequence.find(str(vals_list['invoice_date']).split('-')[1]) > -1:
                    month = datetime.now().month
                    str_month = str(datetime.now().month)
                    if month < 10:
                        str_month = str(0) + str_month
                    idx = split_seq.index(str_month)
                    split_seq[idx] = str(vals_list['date_planned_start']).split('-')[1]
                    get_sequence = "/".join(split_seq)

                orginal_sequence = get_sequence.split('/')
                sequence_padding = get_sequence_object.padding
                get_highest_sequence_no = 0
                if get_highest_manufacture:
                    highest_seq = get_highest_manufacture.name.split('/')
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
                get_sequence_object.number_next_actual = int(get_highest_sequence_no) + 2
                get_sequence = "/".join(orginal_sequence)
            if 'date_planned_start' not in vals_list.keys() and not isinstance(self.date_planned_start,
                                                                       bool):
                if get_sequence.find(str(datetime.now().year)) > -1:
                    idx = split_seq.index(str(datetime.now().year))
                    split_seq[idx] = str(self.date_planned_start).split('-')[0]
                    get_sequence = "/".join(split_seq)
                if get_sequence.find(str(datetime.now().month)) > -1:
                    # if not get_sequence.find(str(vals_list['invoice_date']).split('-')[1]) > -1:
                    month = datetime.now().month
                    str_month = str(datetime.now().month)
                    if month < 10:
                        str_month = str(0) + str_month
                    idx = split_seq.index(str_month)
                    split_seq[idx] = str(self.date_planned_start).split('-')[1]
                    get_sequence = "/".join(split_seq)

                orginal_sequence = get_sequence.split('/')
                sequence_padding = get_sequence_object.padding
                get_highest_sequence_no = 0
                if get_highest_manufacture:
                    highest_seq = get_highest_manufacture.name.split('/')
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
                get_sequence_object.number_next_actual = int(get_highest_sequence_no) + 2
                get_sequence = "/".join(orginal_sequence)
            return get_sequence

        elif '/%(year)s/%(month)s/' in get_sequence_object.prefix and get_sequence_object.sequence_pattern == 'month_year_monthly':
            split_seq_obj = get_sequence_object.prefix.split('/')
            get_year_index = split_seq_obj.index('%(year)s')
            get_month_index = split_seq_obj.index('%(month)s')
            split_inv_name = []
            for i in range(get_year_index + 3):
                split_inv_name.append('')

            if manufacture_name != '':
                split_inv_name = manufacture_name.split('/')
                split_seq = get_sequence.split('/')
                split_inv_name_last_value = split_inv_name[-1]
                split_seq[-1] = split_inv_name_last_value
                if get_highest_manufacture and get_highest_manufacture.name != '/':
                    split_highest_inv = get_highest_manufacture.name.split('/')
                    # get_sequence_object.number_next_actual=int(split_highest_inv[-1])+1
                    # get_sequence_object.number_next_actual = get_sequence_object.number_next_actual - 2
                    get_sequence_object.number_next_actual = get_sequence_object.number_next_actual - 1
            else:
                split_seq = get_sequence.split('/')
                # get_sequence_object.number_next_actual = get_sequence_object.number_next_actual - 2
                get_sequence_object.number_next_actual = get_sequence_object.number_next_actual - 1
                # split_highest_inv = get_highest_inv.split('/')
                # get_sequence_object.number_next_actual = int(split_highest_inv[-1]) + 1
            if 'date_planned_start' in vals_list.keys() and not isinstance(vals_list['date_planned_start'],
                                                                   bool):
                date_obj = datetime.strptime(vals_list['date_planned_start'], '%Y-%m-%d %H:%M:%S') + timedelta(hours=6)

                if get_sequence.find(str(datetime.now().year)) > -1:
                    idx = split_seq.index(str(datetime.now().year))
                    split_seq[idx] = str(date_obj).split('-')[0]
                    get_sequence = "/".join(split_seq)
                if get_sequence.find(str(datetime.now().month)) > -1:
                    # if not get_sequence.find(str(vals_list['invoice_date']).split('-')[1]) > -1:
                    month = datetime.now().month
                    str_month = str(datetime.now().month)
                    if month < 10:
                        str_month = str(0) + str_month
                    idx = split_seq.index(str_month)
                    split_seq[idx] = str(date_obj).split('-')[1]
                    get_sequence = "/".join(split_seq)

                    # region Month wise sequence
                    orginal_sequence = get_sequence.split('/')
                    split_sequence_prefix = get_sequence.split('/')
                    without_last_index = split_sequence_prefix.pop()
                    without_last_index_sequence = "/".join(split_sequence_prefix)
                    without_last_index_sequence += "/"
                    if str(date_obj.date().year) == split_inv_name[get_year_index] and date_obj.date().month == int(split_inv_name[get_month_index]):
                        orginal_sequence = manufacture_name.split('/')
                    else:
                        get_highest_sequence = common_method.get_highest_seq_for_month_year_monthly(get_sequence_object,
                                                                                                    date_obj, model)

                        # get_highest_sequence = self.env['mrp.production'].search(
                        #     [('name', 'like', without_last_index_sequence),
                        #      ('id', '!=', self.id)],
                        #     order="name desc",
                        #     limit=1)
                        sequence_padding = get_sequence_object.padding
                        get_highest_sequence_no = 0
                        if get_highest_sequence:
                            highest_seq = get_highest_sequence.name.split('/')
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
            if 'date_planned_start' not in vals_list.keys() and not isinstance(self.date_planned_start,
                                                                       bool):
                date_obj = self.date_planned_start + timedelta(hours=6)
                if get_sequence.find(str(datetime.now().year)) > -1:
                    idx = split_seq.index(str(datetime.now().year))
                    split_seq[idx] = str(date_obj).split('-')[0]
                    get_sequence = "/".join(split_seq)
                if get_sequence.find(str(datetime.now().month)) > -1:
                    # if not get_sequence.find(str(vals_list['invoice_date']).split('-')[1]) > -1:
                    month = datetime.now().month
                    str_month = str(datetime.now().month)
                    if month < 10:
                        str_month = str(0) + str_month
                    idx = split_seq.index(str_month)
                    split_seq[idx] = str(date_obj).split('-')[1]
                    get_sequence = "/".join(split_seq)
                    # region Month wise sequence
                    orginal_sequence = get_sequence.split('/')
                    split_sequence_prefix = get_sequence.split('/')
                    without_last_index = split_sequence_prefix.pop()
                    without_last_index_sequence = "/".join(split_sequence_prefix)
                    without_last_index_sequence += "/"

                    if str(date_obj.year) == split_inv_name[get_year_index] and date_obj.month == int(
                            split_inv_name[get_month_index]):
                        orginal_sequence = manufacture_name.split('/')
                    else:
                        get_highest_sequence = common_method.get_highest_seq_for_month_year_monthly(get_sequence_object,
                                                                                                    date_obj, model)

                        # get_highest_sequence = self.env['mrp.production'].search(
                        #     [('name', 'like', without_last_index_sequence),
                        #      ('id', '!=', self.id)],
                        #     order="name desc",
                        #     limit=1)
                        sequence_padding = get_sequence_object.padding
                        get_highest_sequence_no = 0
                        if get_highest_sequence:
                            highest_seq = get_highest_sequence.name.split('/')
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

        elif '/%(year)s/%(month)s/' not in get_sequence_object.prefix and '/%(year)s/' in get_sequence_object.prefix and get_sequence_object.sequence_pattern == 'year':
            if manufacture_name != '':
                split_inv_name = manufacture_name.split('/')
                split_seq = get_sequence.split('/')
                split_inv_name_last_value = split_inv_name[-1]
                split_seq[-1] = split_inv_name_last_value
                if get_highest_manufacture and get_highest_manufacture.name != '/':
                    split_highest_inv = get_highest_manufacture.name.split('/')
                    # get_sequence_object.number_next_actual=int(split_highest_inv[-1])+1
                    get_sequence_object.number_next_actual = get_sequence_object.number_next_actual - 1
            else:
                split_seq = get_sequence.split('/')
            if 'date_planned_start' in vals_list.keys() and not isinstance(vals_list['date_planned_start'],
                                                                   bool):
                if get_sequence.find(str(datetime.now().year)) > -1:
                    # highest_seq_last_idx_value="00000"
                    if get_highest_manufacture:
                        highest_seq_last_idx_value=get_highest_manufacture.name.split('/')[-1]
                        idx = split_seq.index(str(datetime.now().year))
                        split_seq[idx] = str(vals_list['date_planned_start']).split('-')[0]
                        split_seq[-1] = highest_seq_last_idx_value
                        get_sequence = "/".join(split_seq)


                    orginal_sequence = get_sequence.split('/')
                    sequence_padding = get_sequence_object.padding
                    get_highest_sequence_no = 0
                    if get_highest_manufacture:
                        highest_seq = get_highest_manufacture.name.split('/')
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
                    get_sequence_object.number_next_actual = int(get_highest_sequence_no) + 2
                    get_sequence = "/".join(orginal_sequence)

            if 'date_planned_start' not in vals_list.keys() and not isinstance(self.date_planned_start,
                                                                       bool):
                if get_sequence.find(str(datetime.now().year)) > -1:
                    highest_seq_last_idx_value = get_highest_manufacture.name.split('/')[-1]
                    idx = split_seq.index(str(datetime.now().year))
                    split_seq[idx] = str(self.date_planned_start).split('-')[0]
                    split_seq[-1]=highest_seq_last_idx_value
                    get_sequence = "/".join(split_seq)
                    orginal_sequence = get_sequence.split('/')
                    sequence_padding = get_sequence_object.padding
                    get_highest_sequence_no = 0
                    if get_highest_manufacture:
                        highest_seq = get_highest_manufacture.name.split('/')
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
                    get_sequence_object.number_next_actual = int(get_highest_sequence_no) + 2
                    get_sequence = "/".join(orginal_sequence)

            return get_sequence

        elif '/%(year)s/%(month)s/' not in get_sequence_object.prefix and '/%(year)s/' in get_sequence_object.prefix and get_sequence_object.sequence_pattern == 'year_yearly':
            split_seq_obj = get_sequence_object.prefix.split('/')
            get_year_index = split_seq_obj.index('%(year)s')
            split_inv_name = []
            for i in range(get_year_index + 1):
                split_inv_name.append('')
            split_inv_name.append('')
            if manufacture_name != '':
                split_inv_name = manufacture_name.split('/')
                split_seq = get_sequence.split('/')
                split_inv_name_last_value = split_inv_name[-1]
                split_seq[-1] = split_inv_name_last_value
                if get_highest_manufacture and get_highest_manufacture.name != '/':
                    split_highest_inv = get_highest_manufacture.name.split('/')
                    # get_sequence_object.number_next_actual = int(split_highest_inv[-1]) + 1
                    get_sequence_object.number_next_actual = get_sequence_object.number_next_actual - 2
            else:
                split_seq = get_sequence.split('/')
                get_sequence_object.number_next_actual = get_sequence_object.number_next_actual - 2
            if 'date_planned_start' in vals_list.keys() and not isinstance(vals_list['date_planned_start'],
                                                                   bool):
                date_obj = datetime.strptime(vals_list['date_planned_start'], '%Y-%m-%d %H:%M:%S') + timedelta(hours=6)

                if get_sequence.find(str(datetime.now().year)) > -1:
                    idx = split_seq.index(str(datetime.now().year))
                    split_seq[idx] = str(date_obj).split('-')[0]
                    get_sequence = "/".join(split_seq)

                    # region year wise sequence
                    orginal_sequence = get_sequence.split('/')
                    split_sequence_prefix = get_sequence.split('/')
                    without_last_index = split_sequence_prefix.pop()
                    without_last_index_sequence = "/".join(split_sequence_prefix)
                    without_last_index_sequence += "/"

                    # month = datetime.now().month
                    # str_month = str(datetime.now().month)
                    # month_sequence_list=[]
                    # for mth in range(1,month+1):
                    #     if month < 10:
                    #         str_month =str(0) + str(mth)
                    #
                    #     month_sequence=without_last_index_sequence+str_month
                    #     month_sequence_list.append('%'+month_sequence+'%')
                    #
                    # # get_highest_sequence = self.env['mrp.production'].search(
                    # #     [('name', 'like', without_last_index_sequence),('name','not like',str_month)
                    # #      ('id', '!=', self.id)],
                    # #     order="name desc",
                    # #     limit=1)
                    # query="""select name from mrp_production where name like '{}' and name not like all (array{}) and id!={} order by name desc limit 1""".format('%'+without_last_index_sequence+'%',month_sequence_list,self.id)
                    # self._cr.execute(query=query)
                    # get_highest_sequence=self._cr.fetchone()
                    if str(date_obj.date().year) == split_inv_name[get_year_index]:
                        orginal_sequence = manufacture_name.split('/')
                    else:
                        get_highest_sequence = common_method.get_highest_seq_for_year_yearly(get_sequence_object,
                                                                                                    date_obj, model)
                        sequence_padding = get_sequence_object.padding
                        get_highest_sequence_no = 0
                        if get_highest_sequence:
                            highest_seq = get_highest_sequence[0].split('/')
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

            if 'date_planned_start' not in vals_list.keys() and not isinstance(self.date_planned_start,
                                                                       bool):
                date_obj = self.date_planned_start + timedelta(hours=6)
                if get_sequence.find(str(datetime.now().year)) > -1:
                    idx = split_seq.index(str(datetime.now().year))
                    split_seq[idx] = str(self.date_planned_start).split('-')[0]
                    get_sequence = "/".join(split_seq)

                    # region year wise sequence
                    orginal_sequence = get_sequence.split('/')
                    split_sequence_prefix = get_sequence.split('/')
                    without_last_index = split_sequence_prefix.pop()
                    without_last_index_sequence = "/".join(split_sequence_prefix)
                    without_last_index_sequence += "/"

                    # month = datetime.now().month
                    # str_month = str(datetime.now().month)
                    # month_sequence_list = []
                    # for mth in range(1, month + 1):
                    #     if month < 10:
                    #         str_month = str(0) + str(mth)
                    #
                    #     month_sequence = without_last_index_sequence + str_month
                    #     month_sequence_list.append('%' + month_sequence + '%')
                    #
                    # # get_highest_sequence = self.env['mrp.production'].search(
                    # #     [('name', 'like', without_last_index_sequence),('name','not like',str_month)
                    # #      ('id', '!=', self.id)],
                    # #     order="name desc",
                    # #     limit=1)
                    # query = """select name from mrp_production where name like '{}' and name not like all (array{}) and id!={} order by name desc limit 1""".format(
                    #     '%' + without_last_index_sequence + '%', month_sequence_list, self.id)
                    # self._cr.execute(query=query)
                    # get_highest_sequence = self._cr.fetchone()
                    if str(date_obj.year) == split_inv_name[get_year_index]:
                        orginal_sequence = manufacture_name.split('/')
                    else:
                        get_highest_sequence = common_method.get_highest_seq_for_year_yearly(get_sequence_object,
                                                                                             date_obj, model)

                        sequence_padding = get_sequence_object.padding
                        get_highest_sequence_no = 0
                        if get_highest_sequence:
                            highest_seq = get_highest_sequence[0].name.split('/')
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
            if manufacture_name != '':
                split_inv_name = manufacture_name.split('/')
                split_seq = get_sequence.split('/')
                split_inv_name_last_value = split_inv_name[-1]
                split_seq[-1] = split_inv_name_last_value
                if get_highest_manufacture and get_highest_manufacture.name != '/':
                    split_highest_inv = get_highest_manufacture.name.split('/')
                    get_sequence_object.number_next_actual = int(split_highest_inv[-1]) + 1
            else:
                split_seq = get_sequence.split('/')
            if 'date_planned_start' in vals_list.keys() and not isinstance(vals_list['date_planned_start'],
                                                                   bool):
                if get_sequence.find(str(datetime.now().month)) > -1:
                    # if not get_sequence.find(str(vals_list['invoice_date']).split('-')[1]) > -1:
                    month = datetime.now().month
                    str_month = str(datetime.now().month)
                    if month < 10:
                        str_month = str(0) + str_month
                    idx = split_seq.index(str_month)
                    split_seq[idx] = str(vals_list['date_planned_start']).split('-')[1]
                    get_sequence = "/".join(split_seq)
            if 'date_planned_start' not in vals_list.keys() and not isinstance(self.date_planned_start,
                                                                       bool):

                if get_sequence.find(str(datetime.now().month)) > -1:
                    # if not get_sequence.find(str(vals_list['invoice_date']).split('-')[1]) > -1:
                    month = datetime.now().month
                    str_month = str(datetime.now().month)
                    if month < 10:
                        str_month = str(0) + str_month
                    idx = split_seq.index(str_month)
                    split_seq[idx] = str(self.date_planned_start).split('-')[1]
                    get_sequence = "/".join(split_seq)
            return get_sequence


        else:
            if manufacture_name != '':
                split_inv_name = manufacture_name.split('/')
                split_seq = get_sequence.split('/')
                split_inv_name_last_value = split_inv_name[-1]
                split_seq[-1] = split_inv_name_last_value
                get_sequence = "/".join(split_seq)
                if get_highest_manufacture and get_highest_manufacture.name != '/':
                    split_highest_inv = get_highest_manufacture.name.split('/')
                    # get_sequence_object.number_next_actual = int(split_highest_inv[-1]) + 1
                    get_sequence_object.number_next_actual = get_sequence_object.number_next_actual - 1
            else:
                split_seq = get_sequence.split('/')
                get_sequence = "/".join(split_seq)

                orginal_sequence = get_sequence.split('/')
                sequence_padding = get_sequence_object.padding
                get_highest_sequence_no = 0
                if get_highest_manufacture:
                    highest_seq = get_highest_manufacture.name.split('/')
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
                get_sequence_object.number_next_actual = int(get_highest_sequence_no) + 2
                get_sequence = "/".join(orginal_sequence)

            return get_sequence