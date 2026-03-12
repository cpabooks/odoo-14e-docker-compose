

import imghdr
import json
import functools
import io
import datetime
import odoo
import os
import tempfile
import sys
import logging
import re
import jinja2
import werkzeug
import werkzeug.utils
import werkzeug.wrappers
import werkzeug.wsgi
from odoo.tools.misc import str2bool, xlwt, file_open
from odoo.tools import topological_sort, html_escape, pycompat
from collections import OrderedDict
from werkzeug.urls import url_decode, iri_to_uri
from odoo.api import call_kw, Environment
from odoo import http, tools,SUPERUSER_ID
from odoo.addons.web.controllers.main import Database, Binary
from odoo.http import content_disposition, dispatch_rpc, request, \
    serialize_exception as _serialize_exception, Response
from odoo.addons.web.controllers import main
from odoo.modules import get_resource_path
from odoo.http import request
from odoo.service import db


_logger = logging.getLogger(__name__)
if hasattr(sys, 'frozen'):
    # When running on compiled windows binary, we don't have access to package loader.
    path = os.path.realpath(os.path.join(os.path.dirname(__file__), '..', 'views'))
    loader = jinja2.FileSystemLoader(path)
else:
    loader = jinja2.PackageLoader('odoo.addons.web_dbrestrict', "views")

env = jinja2.Environment(loader=loader, autoescape=True)
env.filters["json"] = json.dumps

# 1 week cache for asset bundles as advised by Google Page Speed
BUNDLE_MAXAGE = 60 * 60 * 24 * 7

DBNAME_PATTERN = '^[a-zA-Z0-9][a-zA-Z0-9_.-]+$'

# ----------------------------------------------------------
# Odoo Web helpers
# ----------------------------------------------------------

db_list = http.db_list

db_monodb = http.db_monodb

def module_installed(environment):
    # Candidates module the current heuristic is the /static dir
    loadable = list(http.addons_manifest)

    # Retrieve database installed modules
    # TODO The following code should move to ir.module.module.list_installed_modules()
    Modules = environment['ir.module.module']
    domain = [('state','=','installed'), ('name','in', loadable)]
    modules = OrderedDict(
        (module.name, module.dependencies_id.mapped('name'))
        for module in Modules.search(domain)
    )

    sorted_modules = topological_sort(modules)
    return sorted_modules

def abort_and_redirect(url):
    r = request.httprequest
    response = werkzeug.utils.redirect(url, 302)
    response = r.app.get_response(r, response, explicit_session=False)
    werkzeug.exceptions.abort(response)

def ensure_db(redirect='/web/database/selector'):
    # This helper should be used in web client auth="none" routes
    # if those routes needs a db to work with.
    # If the heuristics does not find any database, then the users will be
    # redirected to db selector or any url specified by `redirect` argument.
    # If the db is taken out of a query parameter, it will be checked against
    # `http.db_filter()` in order to ensure it's legit and thus avoid db
    # forgering that could lead to xss attacks.
    db = request.params.get('db') and request.params.get('db').strip()

    # Ensure db is legit
    if db and db not in http.db_filter([db]):
        db = None

    if db and not request.session.db:
        # User asked a specific database on a new session.
        # That mean the nodb router has been used to find the route
        # Depending on installed module in the database, the rendering of the page
        # may depend on data injected by the database route dispatcher.
        # Thus, we redirect the user to the same page but with the session cookie set.
        # This will force using the database route dispatcher...
        r = request.httprequest
        url_redirect = werkzeug.urls.url_parse(r.base_url)
        if r.query_string:
            # in P3, request.query_string is bytes, the rest is text, can't mix them
            query_string = iri_to_uri(r.query_string)
            url_redirect = url_redirect.replace(query=query_string)
        request.session.db = db
        abort_and_redirect(url_redirect)

    # if db not provided, use the session one
    if not db and request.session.db and http.db_filter([request.session.db]):
        db = request.session.db

    # if no database provided and no database in session, use monodb
    if not db:
        db = db_monodb(request.httprequest)

    # if no db can be found til here, send to the database selector
    # the database selector will redirect to database manager if needed
    if not db:
        werkzeug.exceptions.abort(werkzeug.utils.redirect(redirect, 303))

    # always switch the session to the computed db
    if db != request.session.db:
        request.session.logout()
        abort_and_redirect(request.httprequest.url)

    request.session.db = db

def module_installed_bypass_session(dbname):
    try:
        registry = odoo.registry(dbname)
        with registry.cursor() as cr:
            return module_installed(
                environment=Environment(cr, odoo.SUPERUSER_ID, {}))
    except Exception:
        pass
    return {}

def module_boot(db=None):
    server_wide_modules = odoo.conf.server_wide_modules or ['web']
    serverside = []
    dbside = []
    for i in server_wide_modules:
        if i in http.addons_manifest:
            serverside.append(i)
    monodb = db or db_monodb()
    if monodb:
        dbside = module_installed_bypass_session(monodb)
        dbside = [i for i in dbside if i not in serverside]
    addons = serverside + dbside
    return addons


class MyDatabase(Database):

    def _render_template(self, **d):
        d.setdefault('manage', True)
        d['insecure'] = odoo.tools.config.verify_admin_password('admin')
        d['list_db'] = odoo.tools.config['list_db']
        d['langs'] = odoo.service.db.exp_list_lang()
        d['countries'] = odoo.service.db.exp_list_countries()
        d['pattern'] = DBNAME_PATTERN
        # databases list
        d['databases'] = []
        try:
            d['databases'] = http.db_list()
            d['incompatible_databases'] = odoo.service.db.list_db_incompatible(d['databases'])
        except odoo.exceptions.AccessDenied:
            monodb = db_monodb()
            if monodb:
                d['databases'] = [monodb]
        return env.get_template("database_manager.html").render(d)

    @http.route('/web/database/selector', type='http', auth="none")
    def selector(self, **kw):
        request._cr = None
        return self._render_template(manage=False)

    @http.route('/web/database/manager', type='http', auth="none")
    def manager(self, **kw):
        request.session.logout()
        return http.local_redirect('/web/password')

    @http.route('/web/password', type='http', auth='public', website=True)
    def pasword(self, redirect=None, **post):
        return request.render('web_dbrestrict.manager_password', {'url_root': request.httprequest.url_root})

    @http.route('/web/manager', type='http', auth='public', website=True, csrf=False)
    def dbmanager_password(self, **kw):
        ensure_db()
        if not request.uid:
            request.uid = odoo.SUPERUSER_ID

        values = request.params.copy()
        try:
            values['databases'] = http.db_list()
        except odoo.exceptions.AccessDenied:
            values['databases'] = None

        if request.httprequest.method == 'POST':
            uid = request.session.authenticate(request.session.db, request.params['login'], request.params['password'])
            if uid is not False and uid == SUPERUSER_ID:
                request.params['login_success'] = True
                return self._render_template()
            else:
                values = request.params.copy()
                values['error'] = "Only super administrator can access"
                return request.render('web_dbrestrict.manager_password', values)
        else:
            values = request.params.copy()
            values['error'] = "Wrong password"
            return request.render('web_dbrestrict.manager_password', values)







