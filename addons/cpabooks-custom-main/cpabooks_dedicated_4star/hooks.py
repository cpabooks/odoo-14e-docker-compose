# hooks.py
from odoo.tools import sql


def pre_init_hook(cr):
    """
    This runs BEFORE the module is installed
    Adds database columns before any code or views try to access them
    """
    # Add columns to res_partner
    if not sql.column_exists(cr, 'res_partner', 'whatsapp_number'):
        cr.execute('ALTER TABLE res_partner ADD COLUMN whatsapp_number VARCHAR')

    if not sql.column_exists(cr, 'res_partner', 'customer_code'):
        cr.execute('ALTER TABLE res_partner ADD COLUMN customer_code VARCHAR')

    # Add columns to res_company if needed
    if not sql.column_exists(cr, 'res_company', 'whatsapp_number'):
        cr.execute('ALTER TABLE res_company ADD COLUMN whatsapp_number VARCHAR')


def post_init_hook(cr, registry):
    """
    This runs AFTER the module is installed
    Use for any post-installation setup
    """
    pass


def uninstall_hook(cr, registry):
    """
    This runs when the module is uninstalled
    Optional: Remove the columns if you want
    """
    # cr.execute('ALTER TABLE res_partner DROP COLUMN IF EXISTS whatsapp_number')
    # cr.execute('ALTER TABLE res_partner DROP COLUMN IF EXISTS customer_code')