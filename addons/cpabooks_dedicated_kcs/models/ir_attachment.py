import requests
from odoo import api, models, fields, _

class IrAttachment(models.Model):
    _inherit = 'ir.attachment'

    def _pdf_finder(self):
        # Use SQL query to fetch attachments with mimetype 'application/pdf'
        self.env.cr.execute("""
            SELECT id
            FROM ir_attachment
            WHERE mimetype = 'application/pdf'
        """)
        pdf_attachment_ids = [row[0] for row in self.env.cr.fetchall()]

        # Return records corresponding to the fetched ids
        return self.env['ir.attachment'].browse(pdf_attachment_ids)


    def _compute_size(self):
        # Fetch PDF records using SQL
        pdf_records = self._pdf_finder()
        pdf_ids = pdf_records.ids  # List of PDF attachment IDs
        counter = 0
        for rec in self:
            if rec.id in pdf_ids:  # Check if the record is a PDF
                counter += 1
                print(f"{counter}. Processing PDF: {rec.id}")
                try:
                    # Fetch the content of the file at the URL
                    response = requests.head(rec.url, allow_redirects=True)

                    # Check if the content length is in headers
                    content_length = response.headers.get('Content-Length')
                    if content_length:
                        size_in_bytes = int(content_length)
                    else:
                        # Fallback if 'Content-Length' is not available
                        response = requests.get(rec.url, stream=True)
                        size_in_bytes = sum(len(chunk) for chunk in response.iter_content(1024))

                    # Convert size to KB or MB for readability
                    if size_in_bytes < 1024:
                        rec.size = f"{size_in_bytes} B"
                    elif size_in_bytes < 1024 * 1024:
                        rec.size = f"{size_in_bytes / 1024:.2f} KB"
                    else:
                        rec.size = f"{size_in_bytes / (1024 * 1024):.2f} MB"
                except requests.RequestException as e:
                    # Log the error and set size to 0 if there's an issue fetching the file
                    rec.size = "0 B"
            else:
                rec.size = "TYPE IS NOT PDF"

    size = fields.Char('Size', compute=_compute_size)
