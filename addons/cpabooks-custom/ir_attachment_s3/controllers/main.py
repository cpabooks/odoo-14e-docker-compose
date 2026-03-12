from odoo.http import request
from werkzeug import urls, utils
import logging

_logger = logging.getLogger(__name__)

# Try to import ShareRoute; if not present (Community edition), ignore
try:
    from odoo.addons.documents.controllers.main import ShareRoute
except ImportError:
    ShareRoute = None
    _logger.warning("Documents module not installed, ShareRoute override disabled")

if ShareRoute:
    class ShareRouteInherit(ShareRoute):
        """Inherit Documents ShareRoute to customize binary content handling."""

        def binary_content(
                self, id, env=None, field='datas', share_id=None, share_token=None,
                download=False, unique=False, filename_field='name'
        ):
            return super(ShareRouteInherit, self).binary_content(
                id, env, field, share_id, share_token, download, unique, filename_field
            )

        def _get_file_response(self, id, field='datas', share_id=None, share_token=None):
            status, headers, content = self.binary_content(
                id, field=field, share_id=share_id, share_token=share_token, download=True
            )

            if status != 200:
                res = request.env['ir.attachment'].sudo().search([('res_id', '=', id)], limit=1)
                if res and res.url:
                    url = urls.url_parse(res.url)
                    url_params = url.decode_query()
                    url = url.replace(query=urls.url_encode(url_params)).to_url()
                    return utils.redirect(url)

            return super(ShareRouteInherit, self)._get_file_response(id, field, share_id, share_token)
