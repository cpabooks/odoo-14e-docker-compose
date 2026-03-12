from odoo import models, fields, api
PREFIX = "s3://"

class IrAttachmentRestore(models.Model):
    _name = "ir.attachment.restore"
    _description = "Backup for Deleted Attachments"

    name = fields.Char(string="Name")
    url = fields.Char("URL")
    mime_type = fields.Char("Mime Type")
    res_model = fields.Char("Resource Model")
    res_field = fields.Char("Resource Field")
    res_id = fields.Integer("Resource ID")
    res_name = fields.Char("Resource Name")
    attachment_id = fields.Many2one("ir.attachment", "Original Attachment")

    def restore_attachment(self):

        existing_attachment = self.env["ir.attachment"].sudo().search([
            ("res_id", "=", self.res_id),
        ])

        if existing_attachment:

            return

        Attachment = self.env["ir.attachment"].sudo()

        attachment = Attachment.create({
            "name": self.name or "A",
            "type": "url",
            "url": self.url,
            "mimetype": self.mime_type,
            "res_model": self.res_model,
            "res_field": self.res_field,
            "res_id": self.res_id,
            "res_name": self.res_name,
        })
        return attachment

