from odoo import models, fields, api, _
import os
import logging
from odoo.tools.safe_eval import safe_eval

_logger = logging.getLogger(__name__)


class FileCleanupWizard(models.TransientModel):
    _name = 'file.cleanup.wizard'
    _description = "Wizard to cleanup S3 attachments"

    @api.model
    def delete_local_attachments(self):
        """Cleanup attachments from local storage that are stored in S3."""
        # get condition from config
        s3_condition = self.env["ir.config_parameter"].sudo().get_param("s3.condition")
        condition = safe_eval(s3_condition, mode="eval") if s3_condition else []

        # domain for attachments to delete
        domain = condition + [
            ("res_model", "not in", ["ir.ui.view", "ir.ui.menu", "res.company", "res.users"]),
            ("res_model", "!=", False)
        ]

        attachments = self.env['ir.attachment'].search(domain)

        for attachment in attachments:
            if self.is_stored_in_s3(attachment):
                try:
                    file_path = attachment._full_path(attachment.store_fname)
                    if os.path.exists(file_path):
                        os.unlink(file_path)
                        # Optionally clear store_fname if needed
                        # attachment.write({'store_fname': None})
                    self.env.cr.commit()
                except Exception as e:
                    _logger.error('Failed to delete file: %s', e)
                    continue

    def is_stored_in_s3(self, attachment):
        """Check if attachment is stored in S3."""
        return bool(attachment.url)
