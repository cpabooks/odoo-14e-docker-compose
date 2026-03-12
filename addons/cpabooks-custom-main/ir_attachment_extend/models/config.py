
import logging
from odoo import _, api, fields, models

PREFIX = "s3://"

class S3Settings(models.TransientModel):
    _inherit = "res.config.settings"

    def restore_s3_attachments(self):
        backup_attachments = self.env["ir.attachment.restore"].search([])  # Fetch all backup records

        if not backup_attachments:
            return
        for backup in backup_attachments:
            backup.restore_attachment()


