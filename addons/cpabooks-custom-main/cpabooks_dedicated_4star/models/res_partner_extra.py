from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError


class ResPartnerInherit(models.Model):
    _inherit = 'res.partner'

    def action_additional_info(self):
        self.ensure_one()
        Info = self.env['res.partner.extra']

        info_id = Info.sudo().search([
            ('partner_id', '=', self.id)
        ], limit=1)
        if info_id:
            info_id.write({
                'partner_name': self.name
            })

        if not info_id:
            info_id = Info.create({
                'partner_id': self.id,
                'partner_name': self.name
            })

        return {
            'name': f'Additional info for {self.name}',
            'type': 'ir.actions.act_window',
            'res_model': 'res.partner.extra',
            'view_mode': 'form',
            'view_id': self.env.ref('cpabooks_dedicated_4star.view_res_partner_extra_form').id,
            'res_id': info_id.id,
            'target': 'new',
        }

    def action_reset_code(self):
        all_partners = self.sudo().search([], order="id asc")
        for partner in all_partners:
            Info = self.env['res.partner.extra']
            additional_info = Info.sudo().search([
                ('partner_id', '=', partner.id)
            ], limit=1)
            setup = self.env['customer.code.setup'].sudo().search([], limit=1)
            if not additional_info:
                if not setup.code_active:
                    raise UserError(_('Please Activate the code Setup First! \n'
                                      '"Contacts > Configuration > Customer Code Setup"'))
                Info.sudo().create({
                    'partner_id': partner.id,
                    'partner_name': partner.name,
                    'customer_code': setup.get_next_code()
                })
            elif additional_info and not additional_info.customer_code:
                additional_info.customer_code = setup.get_next_code()

            if additional_info:
                additional_info.write({
                    'partner_name': partner.name
                })



class ResPartnerExtra(models.Model):
    _name = 'res.partner.extra'
    _description = 'Partner Additional Info'

    partner_id = fields.Many2one('res.partner', 'Partner', required=True, ondelete='cascade')
    address_line_1 = fields.Char('Address line 1', compute='_compute_address', inverse='_inverse_address', store=False)
    address_line_2 = fields.Char('Address line 2', compute='_compute_address', inverse='_inverse_address', store=False)
    territory = fields.Char('Territory', compute='_compute_address', inverse='_inverse_address', store=False)
    whatsapp_number = fields.Char(string='WhatsApp Number', help='Please Provide WhatsApp number')
    customer_code = fields.Char(string='Customer Code', help='Customer Code')
    care_of = fields.Char('Care of', help='Care of')
    payment_terms_id = fields.Many2one('account.payment.term', 'Payment Terms')
    is_hide_gen_method = fields.Boolean('Hide Method', compute='_compute_id_hide_gen_method')
    partner_name = fields.Char('Name')



    @api.depends('customer_code')
    def _compute_id_hide_gen_method(self):
        for rec in self:
            if not rec.customer_code or rec.customer_code == '':
                rec.is_hide_gen_method = False
            else:
                rec.is_hide_gen_method = True

    def action_generate_code(self):
        code_setup = self.env['customer.code.setup'].search([
            ('company_id', '=', self.env.company.id)
        ], limit=1)

        if code_setup:
            if not code_setup.code_active:
                raise ValidationError(_('Please Activate the code Setup First! \n '
                                        '"Contacts > Configuration > Customer Code Setup"'))
            else:
                self.customer_code = code_setup.get_next_code()
        return {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'res_id': self.id,
            'view_mode': 'form',
            'view_id': False,  # This will use the default form view
            'target': 'new',
            'views': [[False, 'form']],
        }

    @api.depends('partner_id.street', 'partner_id.street2', 'partner_id.city')
    def _compute_address(self):
        for rec in self:
            if rec.partner_id:
                rec.address_line_1 = rec.partner_id.street
                rec.address_line_2 = rec.partner_id.street2
                rec.territory = rec.partner_id.city  # Fixed: should assign to rec.territory, not rec.partner_id.city
            else:
                rec.address_line_1 = False
                rec.address_line_2 = False
                rec.territory = False

    def _inverse_address(self):
        for rec in self:
            if rec.partner_id:
                # Update partner address fields
                if rec.address_line_1:
                    rec.partner_id.street = rec.address_line_1
                if rec.address_line_2:
                    rec.partner_id.street2 = rec.address_line_2
                if rec.territory:
                    rec.partner_id.city = rec.territory

    @api.model
    def create(self, vals):
        res = super(ResPartnerExtra, self).create(vals)
        if not res.customer_code:
            # Get the next customer code
            code_setup = self.env['customer.code.setup'].search([
                ('company_id', '=', self.env.company.id)
            ], limit=1)
            if code_setup:
                res.customer_code = code_setup.get_next_code()
        return res

    def action_save(self):
        """Save and close the wizard"""
        self.ensure_one()
        # The inverse methods will automatically update the partner when fields are changed
        return {'type': 'ir.actions.act_window_close'}