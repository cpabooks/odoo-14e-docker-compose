from odoo import models, fields, api

class IrAttachment(models.Model):
    _inherit = 'ir.attachment'

    def unlink(self):
        for attachment in self:
            self.env["ir.attachment.restore"].create({
                "name": attachment.name,
                "url": attachment.url,
                "mime_type": attachment.mimetype,
                "res_model": attachment.res_model,
                "res_field": attachment.res_field,
                "res_id": attachment.res_id,
                "res_name": attachment.res_name,
                "attachment_id": attachment.id
            })

        return super(IrAttachment, self).unlink()
