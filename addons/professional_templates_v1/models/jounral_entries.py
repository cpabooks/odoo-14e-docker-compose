from odoo import api, models, fields
import calendar

class JournalEntries(models.Model):
    _inherit = 'account.move'

    is_repeat = fields.Boolean('Repeat Entry')
    repeat_count = fields.Integer('Number Of Repeat', default=3)

    def action_post(self):
        """Override post to repeat entries after posting"""
        res = super(JournalEntries, self).action_post()
        if self.is_repeat and self.repeat_count > 0:
            return self.action_repeat()
        return res

    def action_copy_method(self):
        print('test case')

    def action_repeat(self):
        """Create repeated copies of the journal entry with updated dates"""
        self.ensure_one()
        exclude_fields = {
            'name', 'message_follower_ids', 'message_ids',
            'activity_ids', 'message_attachment_count',
            'is_repeat', 'repeat_count'
        }

        base_date = self.date or fields.Date.context_today(self)
        repeated = {}

        for i in range(1, self.repeat_count):
            new_date = self._add_months_safe(base_date, i)

            default = {}
            for field_name, field in self._fields.items():
                if field_name in exclude_fields:
                    continue

                if not field.copy:
                    value = self[field_name]
                    if field.type == 'many2one':
                        default[field_name] = value.id if value else False
                    elif field.type == 'many2many':
                        default[field_name] = [(6, 0, value.ids)]
                    elif field.type == 'one2many':
                        # Copy one2many lines as new records
                        default[field_name] = [(0, 0, line.copy_data()[0]) for line in value]
                    elif field_name == 'state':
                        default[field_name] = 'draft'
                    else:
                        default[field_name] = value

            # Override date + reset repeat fields
            default.update({
                'date': new_date,
                'is_repeat': False,
                'repeat_count': 0,
            })

            # Create the copy
            cpy = self.create(default)
            cpy.partner_id = self.partner_id.id
            cpy.action_post()
            repeated[cpy.name] = cpy.date

        # Build notification message
        message_lines = [f"{key}: {value}" for key, value in repeated.items()]
        message = f" {self.repeat_count} Repeated Journals Created Successfully.\n {self.name}: {self.date}" + "\n".join(message_lines)

        # Show wizard with message
        msg = self.env['journal.message.wizard'].create({
            'message': message
        })
        return {
            'name': 'Journal Repeat Success',
            'type': 'ir.actions.act_window',
            'res_model': 'journal.message.wizard',
            'res_id': msg.id,
            'view_mode': 'form',
            'target': 'new'
        }

    def _add_months_safe(self, date, months):
        """Add months to a date safely, handling end-of-month cases"""
        target_month = date.month + months
        target_year = date.year + (target_month - 1) // 12
        target_month = ((target_month - 1) % 12) + 1

        day = min(date.day, calendar.monthrange(target_year, target_month)[1])
        return date.replace(year=target_year, month=target_month, day=day)
