from datetime import datetime, timedelta
from decimal import Decimal

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class StockPickingInheritance(models.Model):
    _inherit = 'stock.picking'

    system_admin = fields.Boolean(compute="_get_system_admin")
    name = fields.Char(
        'Reference', default='Draft',
        copy=False, index=True, readonly=True)

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
        res = super(StockPickingInheritance, self).create(vals_list)
        company_id = self.env.company.id

        if res.picking_type_code == 'incoming':
            get_sequence_object = self.env['ir.sequence'].sudo().search(
                [('sequence_for', '=', 'incoming'), ('company_id', 'in', [company_id, False])],
                limit=1, )
            picking_name = ''
            get_sequence = self.env['ir.sequence'].next_by_sequence_for('incoming')
            if get_sequence:
                get_highest_picking = self.env['stock.picking'].sudo().search(
                    [('id', '!=', self.id), ('picking_type_code', '=', 'incoming')], limit=1, order='id desc')
                get_sequence = res._get_sequence_picking(get_sequence_object, get_sequence, vals_list,
                                                         get_highest_picking, picking_name)
            if not get_sequence:
                raise ValidationError(_("Sequence is not set for receive products"))
            res.name = get_sequence or _('/')
        elif res.picking_type_code == 'outgoing':
            # get_sequence = self.env['ir.sequence'].next_by_sequence_for('outgoing')
            get_sequence_object = self.env['ir.sequence'].sudo().search(
                [('sequence_for', '=', 'outgoing'), ('company_id', 'in', [company_id, False])],
                limit=1, )
            picking_name = ''
            get_sequence = self.env['ir.sequence'].next_by_sequence_for('outgoing')
            if get_sequence:
                get_highest_picking = self.env['stock.picking'].sudo().search(
                    [('id', '!=', self.id), ('picking_type_code', '=', 'outgoing')], limit=1, order='id desc')
                get_sequence = res._get_sequence_picking(get_sequence_object, get_sequence, vals_list,
                                                         get_highest_picking,
                                                         picking_name)
            if not get_sequence:
                raise ValidationError(_("Sequence is not set for delivered products"))
            res.name = get_sequence or _('/')
        else:
            # get_sequence = self.env['ir.sequence'].next_by_sequence_for('internal')
            get_sequence_object = self.env['ir.sequence'].sudo().search(
                [('sequence_for', '=', 'internal'), ('company_id', 'in', [company_id, False])],
                limit=1, )
            picking_name = ''
            get_sequence = self.env['ir.sequence'].next_by_sequence_for('internal')
            if get_sequence:
                get_highest_picking = self.env['stock.picking'].sudo().search(
                    [('id', '!=', self.id), ('picking_type_code', '=', 'internal')], limit=1, order='id desc')
                get_sequence = res._get_sequence_picking(get_sequence_object, get_sequence, vals_list,
                                                         get_highest_picking,
                                                         picking_name)
            if not get_sequence:
                raise ValidationError(_("Sequence is not set for transfer products"))
            res.name = get_sequence or _('/')
        return res

    def _get_sequence_picking(self, get_sequence_object, get_sequence, vals_list, get_highest_picking, picking_name):
        common_method = self.env['common.method']
        model = 'stock.picking'
        if '/%(year)s/%(month)s/' in get_sequence_object.prefix and get_sequence_object.sequence_pattern == 'month_year':
            if picking_name != '':
                split_picking_name = picking_name.split('/')
                split_seq = get_sequence.split('/')
                split_picking_name_last_value = split_picking_name[-1]
                split_seq[-1] = split_picking_name_last_value
                if get_highest_picking and get_highest_picking.name != '/':
                    split_highest_inv = get_highest_picking.name.split('/')
                    # get_sequence_object.number_next_actual=int(split_highest_inv[-1])+1
                    get_sequence_object.number_next_actual = get_sequence_object.number_next_actual - 1
                else:
                    get_sequence_object.number_next_actual = get_sequence_object.number_next_actual - 1
            else:
                split_seq = get_sequence.split('/')
                # split_highest_inv = get_highest_picking.split('/')
                # get_sequence_object.number_next_actual = int(split_highest_inv[-1]) + 1
            if 'scheduled_date' in vals_list.keys() and not isinstance(vals_list['scheduled_date'],
                                                                       bool):
                if get_sequence.find(str(datetime.now().year)) > -1:
                    idx = split_seq.index(str(datetime.now().year))
                    split_seq[idx] = str(vals_list['scheduled_date']).split('-')[0]
                    get_sequence = "/".join(split_seq)
                if get_sequence.find(str(datetime.now().month)) > -1:
                    # if not get_sequence.find(str(vals_list['scheduled_date']).split('-')[1]) > -1:
                    month = datetime.now().month
                    str_month = str(datetime.now().month)
                    if month < 10:
                        str_month = str(0) + str_month
                    idx = split_seq.index(str_month)
                    split_seq[idx] = str(vals_list['scheduled_date']).split('-')[1]
                    get_sequence = "/".join(split_seq)
            if 'scheduled_date' not in vals_list.keys() and not isinstance(self.scheduled_date,
                                                                           bool):
                if get_sequence.find(str(datetime.now().year)) > -1:
                    idx = split_seq.index(str(datetime.now().year))
                    split_seq[idx] = str(self.scheduled_date).split('-')[0]
                    get_sequence = "/".join(split_seq)
                if get_sequence.find(str(datetime.now().month)) > -1:
                    # if not get_sequence.find(str(vals_list['scheduled_date']).split('-')[1]) > -1:
                    month = datetime.now().month
                    str_month = str(datetime.now().month)
                    if month < 10:
                        str_month = str(0) + str_month
                    idx = split_seq.index(str_month)
                    split_seq[idx] = str(self.scheduled_date).split('-')[1]
                    get_sequence = "/".join(split_seq)
            return get_sequence

        elif '/%(year)s/%(month)s/' in get_sequence_object.prefix and get_sequence_object.sequence_pattern == 'month_year_monthly':
            split_seq_obj = get_sequence_object.prefix.split('/')
            get_year_index = split_seq_obj.index('%(year)s')
            get_month_index = split_seq_obj.index('%(month)s')
            split_inv_name = []
            for i in range(get_year_index + 3):
                split_inv_name.append('')
            if picking_name != '':
                split_inv_name = picking_name.split('/')
                split_seq = get_sequence.split('/')
                split_inv_name_last_value = split_inv_name[-1]
                split_seq[-1] = split_inv_name_last_value
                if get_highest_picking and get_highest_picking.name != '/':
                    split_highest_inv = get_highest_picking.name.split('/')
                    # get_sequence_object.number_next_actual=int(split_highest_inv[-1])+1
                    get_sequence_object.number_next_actual = get_sequence_object.number_next_actual - 1
                else:
                    get_sequence_object.number_next_actual = get_sequence_object.number_next_actual - 1
            else:
                split_seq = get_sequence.split('/')
                get_sequence_object.number_next_actual = get_sequence_object.number_next_actual - 1
                # split_highest_inv = get_highest_picking.split('/')
                # get_sequence_object.number_next_actual = int(split_highest_inv[-1]) + 1
            if 'scheduled_date' in vals_list.keys() and not isinstance(vals_list['scheduled_date'],
                                                                       bool):
                date_obj = datetime.strptime(vals_list['scheduled_date'], '%Y-%m-%d %H:%M:%S') + timedelta(hours=6)

                if get_sequence.find(str(datetime.now().year)) > -1:
                    idx = split_seq.index(str(datetime.now().year))
                    split_seq[idx] = str(date_obj).split('-')[0]
                    get_sequence = "/".join(split_seq)
                if get_sequence.find(str(datetime.now().month)) > -1:
                    # if not get_sequence.find(str(vals_list['scheduled_date']).split('-')[1]) > -1:
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
                        orginal_sequence = picking_name.split('/')
                    else:
                        get_highest_sequence = common_method.get_highest_seq_for_month_year_monthly(get_sequence_object,
                                                                                                    date_obj, model)

                        # get_highest_sequence = self.env['stock.picking'].search(
                        #     [('name', 'like', without_last_index_sequence + '%'), ('id', '!=', self.id)],
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
            if 'scheduled_date' not in vals_list.keys() and not isinstance(self.scheduled_date,
                                                                           bool):
                date_obj=self.scheduled_date+timedelta(hours=6)
                if get_sequence.find(str(datetime.now().year)) > -1:
                    idx = split_seq.index(str(datetime.now().year))
                    split_seq[idx] = str(date_obj).split('-')[0]
                    get_sequence = "/".join(split_seq)
                if get_sequence.find(str(datetime.now().month)) > -1:
                    # if not get_sequence.find(str(vals_list['scheduled_date']).split('-')[1]) > -1:
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
                        orginal_sequence = picking_name.split('/')
                    else:
                        get_highest_sequence = common_method.get_highest_seq_for_month_year_monthly(get_sequence_object,
                                                                                                    date_obj, model)

                        # get_highest_sequence = self.env['stock.picking'].search(
                        #     [('name', 'like', without_last_index_sequence + '%'), ('id', '!=', self.id)],
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
            if picking_name != '':
                split_inv_name = picking_name.split('/')
                split_seq = get_sequence.split('/')
                split_inv_name_last_value = split_inv_name[-1]
                split_seq[-1] = split_inv_name_last_value
                # if get_highest_picking and get_highest_picking.name!='/':
                #     split_highest_inv=get_highest_picking.name.split('/')
                # get_sequence_object.number_next_actual=int(split_highest_inv[-1])+1
                get_sequence_object.number_next_actual = get_sequence_object.number_next_actual - 1
            else:
                split_seq = get_sequence.split('/')
            if 'scheduled_date' in vals_list.keys() and not isinstance(vals_list['scheduled_date'],
                                                                       bool):
                if get_sequence.find(str(datetime.now().year)) > -1:
                    idx = split_seq.index(str(datetime.now().year))
                    split_seq[idx] = str(vals_list['scheduled_date']).split('-')[0]
                    get_sequence = "/".join(split_seq)

            if 'scheduled_date' not in vals_list.keys() and not isinstance(self.scheduled_date,
                                                                           bool):
                if get_sequence.find(str(datetime.now().year)) > -1:
                    idx = split_seq.index(str(datetime.now().year))
                    split_seq[idx] = str(self.scheduled_date).split('-')[0]
                    get_sequence = "/".join(split_seq)

            return get_sequence

        elif '/%(year)s/%(month)s/' not in get_sequence_object.prefix and '/%(year)s/' in get_sequence_object.prefix and get_sequence_object.sequence_pattern == 'year_yearly':
            split_seq_obj = get_sequence_object.prefix.split('/')
            get_year_index = split_seq_obj.index('%(year)s')
            split_inv_name = []
            for i in range(get_year_index + 1):
                split_inv_name.append('')
            split_inv_name.append('')
            if picking_name != '':
                split_inv_name = picking_name.split('/')
                split_seq = get_sequence.split('/')
                split_inv_name_last_value = split_inv_name[-1]
                split_seq[-1] = split_inv_name_last_value
                # if get_highest_picking and get_highest_picking.name != '/':
                #     split_highest_inv = get_highest_picking.name.split('/')
                # get_sequence_object.number_next_actual = int(split_highest_inv[-1]) + 1
                get_sequence_object.number_next_actual = get_sequence_object.number_next_actual - 1
            else:
                split_seq = get_sequence.split('/')
                get_sequence_object.number_next_actual = get_sequence_object.number_next_actual - 1
            if 'scheduled_date' in vals_list.keys() and not isinstance(vals_list['scheduled_date'],
                                                                       bool):
                date_obj = datetime.strptime(vals_list['scheduled_date'], '%Y-%m-%d %H:%M:%S') + timedelta(hours=6)

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
                    if str(date_obj.date().year) == split_inv_name[get_year_index]:
                        orginal_sequence = picking_name.split('/')
                    else:
                        get_highest_sequence = common_method.get_highest_seq_for_year_yearly(get_sequence_object,
                                                                                             date_obj, model)

                        # get_highest_sequence = self.env['stock.picking'].search(
                        #     [('name', 'like', without_last_index_sequence + '%'), ('id', '!=', self.id)],
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

            if 'scheduled_date' not in vals_list.keys() and not isinstance(self.scheduled_date,
                                                                           bool):
                date_obj = self.scheduled_date + timedelta(hours=6)
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
                    if str(date_obj.year) == split_inv_name[get_year_index]:
                        orginal_sequence = picking_name.split('/')
                    else:
                        get_highest_sequence = common_method.get_highest_seq_for_year_yearly(get_sequence_object,
                                                                                             date_obj, model)
                        #
                        # get_highest_sequence = self.env['stock.picking'].search(
                        #     [('name', 'like', without_last_index_sequence + '%'), ('id', '!=', self.id)],
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
                            # divide_by = 100000
                            # if sequence_padding == 4:
                            #     divide_by = 10000
                            # if sequence_padding == 3:
                            #     divide_by = 1000
                            # if sequence_padding == 2:
                            #     divide_by = 100
                            # if sequence_padding == 1:
                            #     divide_by = 10
                            number = (get_highest_sequence_no + 1) / divide_by
                            dec_string = str(round(Decimal(number), sequence_padding))
                            string_convert = dec_string.split('.')[1]
                            orginal_sequence[-1] = string_convert

                    get_sequence = "/".join(orginal_sequence)
                    # endregion

            return get_sequence

        elif '/%(year)s/%(month)s/' not in get_sequence_object.prefix and '/%(month)s/' in get_sequence_object.prefix:
            if picking_name != '':
                split_inv_name = picking_name.split('/')
                split_seq = get_sequence.split('/')
                split_inv_name_last_value = split_inv_name[-1]
                split_seq[-1] = split_inv_name_last_value
                # if get_highest_picking and get_highest_picking.name != '/':
                #     split_highest_inv = get_highest_picking.name.split('/')
                #     get_sequence_object.number_next_actual = int(split_highest_inv[-1]) + 1
                get_sequence_object.number_next_actual = get_sequence_object.number_next_actual - 1
            else:
                split_seq = get_sequence.split('/')
            if 'scheduled_date' in vals_list.keys() and not isinstance(vals_list['scheduled_date'],
                                                                       bool):
                if get_sequence.find(str(datetime.now().month)) > -1:
                    # if not get_sequence.find(str(vals_list['scheduled_date']).split('-')[1]) > -1:
                    month = datetime.now().month
                    str_month = str(datetime.now().month)
                    if month < 10:
                        str_month = str(0) + str_month
                    idx = split_seq.index(str_month)
                    split_seq[idx] = str(vals_list['scheduled_date']).split('-')[1]
                    get_sequence = "/".join(split_seq)
            if 'scheduled_date' not in vals_list.keys() and not isinstance(self.scheduled_date,
                                                                           bool):

                if get_sequence.find(str(datetime.now().month)) > -1:
                    # if not get_sequence.find(str(vals_list['scheduled_date']).split('-')[1]) > -1:
                    month = datetime.now().month
                    str_month = str(datetime.now().month)
                    if month < 10:
                        str_month = str(0) + str_month
                    idx = split_seq.index(str_month)
                    split_seq[idx] = str(self.scheduled_date).split('-')[1]
                    get_sequence = "/".join(split_seq)
            return get_sequence


        else:
            if picking_name != '':
                split_inv_name = picking_name.split('/')
                split_seq = get_sequence.split('/')
                split_inv_name_last_value = split_inv_name[-1]
                split_seq[-1] = split_inv_name_last_value
                get_sequence = "/".join(split_seq)
                # if get_highest_picking and get_highest_picking.name != '/':
                #     split_highest_inv = get_highest_picking.name.split('/')
                # get_sequence_object.number_next_actual = int(split_highest_inv[-1]) + 1
                get_sequence_object.number_next_actual = get_sequence_object.number_next_actual - 1
            else:
                split_seq = get_sequence.split('/')
                get_sequence = "/".join(split_seq)
            return get_sequence

    def write(self, vals_list):
        print(vals_list)

        rec = super(StockPickingInheritance, self).write(vals_list)
        # if 'name' in vals_list.keys():
        # self_name = self.name.split('/')
        # vals_name = vals_list['name'].split('/')
        # if self_name[0]!=vals_name[0] and self_name[1]!=vals_name[1] and self_name[2]!=vals_name[2]:
        company_id = self.env.company.id
        for res in self:
            picking_name = ''

            if ('scheduled_date' in vals_list.keys() and not isinstance(vals_list['scheduled_date'], bool)) or (
                    res.name == '/' and not isinstance(res.scheduled_date, bool)):
                if res.picking_type_code == 'incoming':
                    get_sequence_object = self.env['ir.sequence'].sudo().search(
                        [('sequence_for', '=', 'incoming'), ('company_id', 'in', [company_id, False])],
                        limit=1, )
                    if res.name != '/' or res.name.upper() != 'DRAFT' or res.name.upper() != 'NEW':
                        picking_name = res.name
                    if res.name == '/' or res.name.upper() == 'DRAFT' or res.name.upper() == 'NEW':
                        picking_name = ''

                    if picking_name != '':
                        get_sequence = self.env['ir.sequence'].next_by_sequence_for('incoming')

                        if get_sequence:
                            get_highest_picking = self.env['stock.picking'].sudo().search(
                                [('id', '!=', self.id), ('picking_type_code', '=', 'incoming')], limit=1,
                                order='id desc')

                            get_sequence = res._get_sequence_picking(get_sequence_object, get_sequence, vals_list,
                                                                     get_highest_picking, picking_name)

                        if not get_sequence:
                            raise ValidationError(_("Sequence is not set for receive products"))
                        res.name = get_sequence or _('/')

                elif res.picking_type_code == 'outgoing':
                    get_sequence_object = self.env['ir.sequence'].sudo().search(
                        [('sequence_for', '=', 'outgoing'), ('company_id', 'in', [company_id, False])],
                        limit=1, )
                    if res.name != '/' or res.name.upper() != 'DRAFT' or res.name.upper() != 'NEW':
                        picking_name = res.name
                    if res.name == '/' or res.name.upper() == 'DRAFT' or res.name.upper() == 'NEW':
                        picking_name = ''

                    if picking_name != '':
                        get_sequence = self.env['ir.sequence'].next_by_sequence_for('outgoing')

                        if get_sequence:
                            get_highest_picking = self.env['stock.picking'].sudo().search(
                                [('id', '!=', self.id), ('picking_type_code', '=', 'outgoing')], limit=1,
                                order='id desc')

                            get_sequence = res._get_sequence_picking(get_sequence_object, get_sequence, vals_list,
                                                                     get_highest_picking, picking_name)

                        if not get_sequence:
                            raise ValidationError(_("Sequence is not set for delivered products"))
                        res.name = get_sequence or _('/')

                else:
                    get_sequence_object = self.env['ir.sequence'].sudo().search(
                        [('sequence_for', '=', 'internal'), ('company_id', 'in', [company_id, False])],
                        limit=1, )
                    if res.name != '/' or res.name.upper() != 'DRAFT' or res.name.upper() != 'NEW':
                        picking_name = res.name
                    if res.name == '/' or res.name.upper() == 'DRAFT' or res.name.upper() == 'NEW':
                        picking_name = ''

                    if picking_name != '':
                        get_sequence = self.env['ir.sequence'].next_by_sequence_for('internal')

                        if get_sequence:
                            get_highest_picking = self.env['stock.picking'].sudo().search(
                                [('id', '!=', self.id), ('picking_type_code', '=', 'internal')], limit=1,
                                order='id desc')

                            get_sequence = res._get_sequence_picking(get_sequence_object, get_sequence, vals_list,
                                                                     get_highest_picking, picking_name)

                        if not get_sequence:
                            raise ValidationError(_("Sequence is not set for transfer products"))
                        res.name = get_sequence or _('/')

        return rec
