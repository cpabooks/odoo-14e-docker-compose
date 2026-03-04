from odoo import models, api, fields


class OdooWhatsapp(models.TransientModel):

    _name = 'odoo.whatsapp.wizard'

    user_id = fields.Many2one("res.partner", string="Recipient")
    mobile = fields.Char(related="user_id.mobile", required=True)
    whatsapp_no =fields.Char(related="user_id.whatsappp_number", string="Whatsapp Number")
    message = fields.Text(string="Message")
    attachment_ids = fields.Many2many('ir.attachment', string='Attachments', copy=False)

    # so_num = fields.Char(string="SALE NO")

#     @api.onchange('user_id')
#     def get_value_from_user(self):
#         self.message = "Hello,"<p/>  + "Your order S00001 amounting in" + self. ₹ has been confirmed.
# Thank you for your trust!"" 

    def send_message(self):
        if self.message and self.whatsapp_no:
            message_string = ''
            message = self.message.split(' ')
            for msg in message:
                message_string = message_string + msg + '%20'
            message_string = message_string[:(len(message_string) - 3)]
            return {
                'type': 'ir.actions.act_url',
                'url': "https://web.whatsapp.com/send?phone="+self.user_id.mobile+"&text=" + message_string,
                'target': '_blank',
                'res_id': self.id,
            }
