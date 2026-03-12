from odoo import api, models, fields, _

class ProductCategoryInherit(models.Model):
    _inherit = 'product.category'

    code_prefix = fields.Char('Prefix')
    code_start = fields.Integer('First Digit', default=1)
    code_padding = fields.Integer('Code Digits', default=4)
    code_step = fields.Integer('Step', default=1)
    code_next = fields.Integer('Next Number', default=1)
    code_last = fields.Char('Last Code')
    code_active = fields.Boolean('Active')

    _sql_constraints = [
        ('name_unique', 'unique(name)', _('Category name must be unique.'))
    ]

    @api.model
    def default_get(self, fields_list):
        res = super(ProductCategoryInherit, self).default_get(fields_list)
        get_last = self.search([], limit=1, order="id desc")
        if get_last:
            num = get_last.code_start + 1
            while self.search([('code_start', '=', num)], limit=1):
                num += 1
            res.update({
                'code_start': num
            })
        return res

    @api.model
    def create(self, vals):
        res = super(ProductCategoryInherit, self).create(vals)
        if res.name:
            res.code_prefix = res.name[:3].upper()
        return res

    def get_next_code(self):
        self.ensure_one()
        if not all([self.code_prefix, self.code_padding, self.code_step, self.code_next, self.code_start, self.code_active]):
            return ''
        next_num = self.code_next
        code = f'{self.code_prefix}_{str(self.code_start)}{str(next_num).zfill(self.code_padding - (len(str(self.code_start)) if len(str(self.code_start)) >= 0 else 0))}'
        next_num += self.code_step
        self.write({
            'code_last': code,
            'code_next': next_num
        })
        return code

    @api.model
    def action_update_code_prefix(self):
        categories = self.search([], order="id asc")
        ser = 0
        for cat in categories:
            vals = {}
            if not cat.code_start or cat.code_start == 1:
                ser += 1
                category = self.search([
                    ('code_start', '=', ser)
                ])
                while self.search([('code_start', '=', ser)], limit=1):
                    ser += 1
                vals.update({
                    'code_start': ser
                })
            if not cat.code_prefix:
                vals.update({
                    'code_prefix': cat.name[:3].upper()
                })
            if vals:
                cat.write(vals)

    def action_active_all(self):
        categories = self.search([])
        for cat in categories:
            cat.code_active = True