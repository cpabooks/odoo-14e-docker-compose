from odoo import models, fields, api
import base64
import logging
import requests

_logger = logging.getLogger(__name__)

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    attachment_id = fields.Many2one('ir.attachment', string="Profile Image Attachment")
    image_1920 = fields.Binary(store=False, compute="_compute_image_1920", inverse="_set_image_1920")
    image_128 = fields.Binary(store=False)

    def _compute_image_1920(self):
        """Dynamically fetch the image from S3 when displaying or from the Odoo database."""
        for record in self:
            if record.attachment_id and record.attachment_id.url:
                # If there's an attachment in S3, show that image
                try:
                    response = requests.get(record.attachment_id.url, timeout=5)
                    if response.status_code == 200:
                        # Add cache-busting parameter to force image reload
                        cache_busting_url = f"{record.attachment_id.url}?{int(fields.Datetime.now().timestamp())}"
                        record.image_1920 = base64.b64encode(response.content)
                    else:
                        record.image_1920 = False
                except Exception as e:
                    _logger.error(f"Failed to load image from S3: {e}")
                    record.image_1920 = False
            elif record.image_1920:
                # If there's an image in the database (storable image), show it
                record.image_1920 = record.image_1920
            else:
                record.image_1920 = False

    def _set_image_1920(self):
        """Handle image upload and store it in S3 or Odoo depending on the condition."""
        for record in self:
            if record.image_1920:
                if record.attachment_id:
                    # If there's already an attachment (stored image), update or replace with S3 image
                    attachment_id = record._upload_image_to_s3(record.image_1920)
                    record.attachment_id = attachment_id
                else:
                    # If no existing attachment, just store in S3
                    attachment_id = record._upload_image_to_s3(record.image_1920)
                    record.attachment_id = attachment_id

                # Clear the cache and force refresh
                record.invalidate_cache(['image_1920'])
                record.env['product.template'].browse(record.id)._compute_image_1920()

                _logger.info(f"Updated profile image for product: {record.name}")

    def _upload_image_to_s3(self, image_data):
        """Uploads the product image to S3 and creates or updates an attachment."""
        Attachment = self.env["ir.attachment"].sudo()
        bucket = self.env["res.config.settings"].get_s3_bucket()

        if not bucket:
            _logger.error("S3 bucket not configured properly.")
            return False

        image_binary = base64.b64decode(image_data)
        file_checksum = self.env["ir.attachment"]._compute_checksum(image_binary)
        file_name = f"product_images/{file_checksum}.png"

        # Upload image to S3
        bucket.put_object(
            Key=file_name,
            Body=image_binary,
            ACL="public-read",
            ContentType="image/png",
        )

        # Generate public URL
        file_url = self.env["res.config.settings"].get_s3_obj_url(bucket, file_name)

        # Check if attachment exists and update it
        attachment = Attachment.search([('res_model', '=', 'product.template'), ('res_id', '=', self.id)], limit=1)
        if attachment:
            attachment.write({
                "url": file_url,
            })
        else:
            attachment = Attachment.create({
                "name": f"Product Image - {self.name}",
                "type": "url",
                "url": file_url,
                "res_model": "product.template",
                "res_id": self.id,
                "mimetype": "image/png",
            })

        # Log the attachment URL
        _logger.info(f"Created or updated attachment with URL: {file_url}")

        return attachment.id
