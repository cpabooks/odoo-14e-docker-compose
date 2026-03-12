import base64
import requests
from odoo import fields, models, api, _


class ProductTemplateInherit(models.Model):
    _inherit = 'product.template'

    link_url = fields.Char("Link URL", compute="_compute_link_url", store=True)
    check_image_db = fields.Boolean('Image', compute="_compute_image_db")

    @api.depends('image_1920')
    def _compute_link_url(self):
        for rec in self:
            Attachment = self.env['ir.attachment'].sudo()
            backup_attachments = Attachment.search([
                ('res_model', '=', 'product.template'),
                ('res_id', '=', rec.id),
                ('url', '!=', False),
                # optionally: ('mimetype', 'ilike', 'image')
            ], limit=1)
            rec.link_url = backup_attachments.url if backup_attachments else False

    @api.depends('link_url')
    def _compute_image_db(self):
        for rec in self:
            if rec.link_url:
                rec.check_image_db = True
            else:
                rec.check_image_db = False

    def action_restore_image_from_db(self):
        Attachment = self.env['ir.attachment'].sudo()
        for rec in self:
            backup = Attachment.search([
                ('res_model', '=', 'product.template'),
                ('res_id', '=', rec.id),
                ('url', '!=', False),
            ], limit=1)
            if backup:
                try:
                    response = requests.get(backup.url, timeout=20)
                    response.raise_for_status()
                except Exception as e:
                    # good to log error
                    continue
                rec.image_1920 = base64.b64encode(response.content)
                img = base64.b64encode(response.content)
                backup.write({'datas': img})
                if backup.datas:
                    print("TRee")
                print("Restored image for product:", rec.id, rec.name)
