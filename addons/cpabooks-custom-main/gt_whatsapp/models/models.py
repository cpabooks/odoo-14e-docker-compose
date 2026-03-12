from odoo import models, fields, api, _


class ResPartner(models.Model):
    _inherit = 'res.partner'

    whatsappp_number=fields.Char(string="Whatsapp No")

    def send_msg(self):
        return {'type': 'ir.actions.act_window',
                'name': _('Whatsapp Message'),
                'res_model': 'odoo.whatsapp.wizard',
                'target': 'new',
                'view_mode': 'form',
                'view_type': 'form',
                'context': {'default_user_id': self.id},
                }


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    additional_note = fields.Char(string='Additional Note')

    def send_whatsapp_msg(self):
        # Find the e-mail template
        template = self.env.ref('sale.email_template_edi_sale')

        # Send out the e-mail template to the user
        self.env['mail.template'].browse(template.id).send_mail(self.id)

        # Find the PDF attachment related to the sale order
        pdf_attachment = self.env['ir.attachment'].search([
            ('res_model', '=', 'mail.message'),
            ('res_name', '=', self.name),
            ('mimetype', '=', 'application/pdf')], limit=1)

        print(f'Name: {self.name}, id: {self.id}')
        print(pdf_attachment)

        message_content = (
            f'Hello, {self.partner_id.name}. \n'
            f'Your Order *{self.name}* amounting in *{self.amount_total}* has been confirmed. \n'
            f'Thank you for your trust! Do not hesitate to contact us if you have any questions.'
        )

        # Prepare default context for WhatsApp wizard
        default_context = {
            'default_user_id': self.partner_id.id,
            'default_message': message_content,
        }

        if pdf_attachment:
            default_context['default_attachment_ids'] = [(4, pdf_attachment.id)]

        return {
            'type': 'ir.actions.act_window',
            'name': _('Whatsapp Message'),
            'res_model': 'odoo.whatsapp.wizard',
            'target': 'new',
            'view_mode': 'form',
            'view_type': 'form',
            'context': default_context,
        }

