from odoo import api, models, fields, _

class CustomerCodeSetup(models.Model):
    _name = 'customer.code.setup'
    _description = 'Customer Code Setup'

    code_prefix = fields.Char('Prefix')
    code_start = fields.Integer('First Digit', default=1)
    code_padding = fields.Integer('Code Digits', default=4)
    code_step = fields.Integer('Step', default=1)
    code_next = fields.Integer('Next Number', default=1)
    code_last = fields.Char('Last Code')
    code_active = fields.Boolean('Active')
    company_id = fields.Many2one('res.company', 'Company')
    separator = fields.Char('Separator', default='-')

    def get_next_code(self):
        self.ensure_one()
        if not all([self.code_prefix, self.code_padding, self.code_step, self.code_next, self.code_start, self.code_active]):
            return ''
        next_num = self.code_next
        code = f'{self.code_prefix}{self.separator}{str(self.code_start)}{str(next_num).zfill(self.code_padding - (len(str(self.code_start)) if len(str(self.code_start)) >= 0 else 0))}'
        next_num += self.code_step
        self.write({
            'code_last': code,
            'code_next': next_num
        })
        return code

    @api.model
    def action_create_setup_data(self):
        cids = self.env['res.company'].sudo().search([])

        for company in cids:
            prefix = ''.join(w[0].upper() for w in company.name.split())
            setup = self.sudo().search([
                ('company_id', '=', company.id)
            ], limit=1)
            if not setup:
                self.create({
                    'code_prefix': prefix,
                    'company_id': company.id
                })

    def action_save(self):
        """Save and close the wizard"""
        self.ensure_one()
        return {'type': 'ir.actions.act_window_close'}

    def get_last_config(self):
        """Return the last created configuration"""
        return self.search([('company_id', '=', self.env.company.id)], order='id desc', limit=1)


    @api.model
    def default_get(self, fields):
        """Override default_get to load the last record's values"""
        res = super(CustomerCodeSetup, self).default_get(fields)

        # Get the last created record
        last_record = self.get_last_config()
        if last_record:
            # Copy values from last record
            for field in ['code_prefix', 'code_start', 'code_padding', 'code_step', 'code_active']:
                if field in fields:
                    res[field] = last_record[field]

        return res
