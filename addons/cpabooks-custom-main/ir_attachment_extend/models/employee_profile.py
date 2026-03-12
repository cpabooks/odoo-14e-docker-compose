# from odoo import models, fields, api
# import base64
# import logging
# import requests
#
# _logger = logging.getLogger(__name__)
#
# class HrEmployee(models.Model):
#     _inherit = 'hr.employee'
#
#     attachment_id = fields.Many2one('ir.attachment', string="Profile Image Attachment")
#     image_1920 = fields.Binary(compute="_compute_image_1920", inverse="_set_image_1920", store=False)
#
#     def _compute_image_1920(self):
#         """Dynamically fetch the image from S3 when displaying."""
#         for record in self:
#             if record.attachment_id and record.attachment_id.url:
#                 try:
#                     response = requests.get(record.attachment_id.url, timeout=5)
#                     if response.status_code == 200:
#                         record.image_1920 = base64.b64encode(response.content)
#                     else:
#                         record.image_1920 = False
#                 except Exception as e:
#                     _logger.error(f"Failed to load image from S3: {e}")
#                     record.image_1920 = False
#             else:
#                 record.image_1920 = False
#
#     def _set_image_1920(self):
#         """Handle image upload and store it in S3."""
#         for record in self:
#             if record.image_1920:
#                 attachment_id = record._upload_image_to_s3(record.image_1920)
#                 record.attachment_id = attachment_id
#
#     def _upload_image_to_s3(self, image_data):
#         """Uploads the employee image to S3 and creates an attachment."""
#         Attachment = self.env["ir.attachment"].sudo()
#         bucket = self.env["res.config.settings"].get_s3_bucket()
#
#         if not bucket:
#             _logger.error("S3 bucket not configured properly.")
#             return False
#
#         image_binary = base64.b64decode(image_data)
#         file_checksum = self.env["ir.attachment"]._compute_checksum(image_binary)
#         file_name = f"employee_images/{file_checksum}.png"
#
#         # Upload image to S3
#         bucket.put_object(
#             Key=file_name,
#             Body=image_binary,
#             ACL="public-read",
#             ContentType="image/png",
#         )
#
#         # Generate public URL
#         file_url = self.env["res.config.settings"].get_s3_obj_url(bucket, file_name)
#
#         # Create an attachment record
#         attachment = Attachment.create({
#             "name": f"Employee Image - {self.name}",
#             "type": "url",
#             "url": file_url,
#             "res_model": "hr.employee",
#             "res_id": self.id,
#             "mimetype": "image/png",
#         })
#
#         return attachment.id