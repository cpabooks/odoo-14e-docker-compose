from odoo import api, models, fields, _
from odoo.exceptions import ValidationError

class DotMatrixTemplate(models.Model):
    _name = 'dot.matrix.template'
    _description = 'Dot Matrix Template Configuration'

    name = fields.Char('Name')
    # page setup
    unit = fields.Selection([
        ('px', 'px'),
        ('mm', 'mm'),
        ('em', 'em'),
        ('rem', 'rem'),
        ('cm', 'cm'),
        ('inch', 'inch'),
    ], 'Unit of Length', default="cm", required=True)
    font_family = fields.Selection([
        ('VT323', 'VT323'),
        ('Share Tech Mono', 'Share Tech Mono'),
        ('Press Start 2P', 'Press Start 2P'),
        ('Courier Prime', 'Courier Prime'),
        ('IBM Plex Mono', 'IBM Plex Mono'),
        ('Roboto', 'Roboto'),
        ('Open Sans', 'Open Sans'),
        ('Montserrat', 'Montserrat'),
        ('Poppins', 'Poppins'),
        ('Lato', 'Lato'),
        ('Nunito', 'Nunito'),
        ('Inter', 'Inter'),
        ('Merriweather', 'Merriweather'),
        ('Playfair Display', 'Playfair Display'),
        ('Raleway', 'Raleway'),
        ('Times New Roman', 'Times New Roman'),
        ('Arial', 'Arial'),
        ('Arial Black', 'Arial Black'),
    ], 'Font Family', default='Share Tech Mono')
    body_font_unit = fields.Selection([
        ('px', 'px'),
        ('mm', 'mm'),
        ('em', 'em'),
        ('rem', 'rem'),
        ('cm', 'cm'),
        ('inch', 'inch'),
    ], 'Unit of Length', default="px", required=True)
    body_font_size = fields.Float('Body Font Size', default=16)
    font_weight = fields.Integer('Font Weight', default=500, help="Recommended Font Width 500-700. Minimum range 500, Maximum range 900")
    email_font_size = fields.Float('Font Size for Email', default=12)

    # Top Left Box
    cust_code_margin_top = fields.Float('Cust. Code Margin Top', default=0.0)
    cust_code_margin_left = fields.Float('Cust. Code Margin Left', default=0.0)
    trn_margin_top = fields.Float('TRN Margin Top', default=0.0)
    trn_margin_left = fields.Float('TRN Margin Left', default=0.0)
    name_margin_top = fields.Float('Name Margin Top', default=0.0)
    name_margin_left = fields.Float('Name Margin Left', default=0.0)
    tel_margin_top = fields.Float('Tel Margin Top', default=0.0)
    tel_margin_left = fields.Float('Tel Margin Left', default=0.0)
    territory_margin_top = fields.Float('Territory Margin Top', default=0.0)
    territory_margin_left = fields.Float('Territory Margin Left', default=0.0)
    mobile_margin_top = fields.Float('Mobile Margin Top', default=0.0)
    mobile_margin_left = fields.Float('Mobile Margin Left', default=0.0)
    whatsapp_margin_top = fields.Float('Whatsapp Margin Top', default=0.0)
    whatsapp_margin_left = fields.Float('Whatsapp Margin Left', default=0.0)
    email_margin_top = fields.Float('Email Margin Top', default=0.0)
    email_margin_left = fields.Float('Email Margin Left', default=0.0)
    emirates_margin_top = fields.Float('Emirates Margin Top', default=0.0)
    emirates_margin_left = fields.Float('Emirates Margin Left', default=0.0)

    # Top Right Box
    inv_margin_top = fields.Float('Invoice Margin Top', default=0.0)
    inv_margin_left = fields.Float('Invoice Margin Left', default=0.0)
    date_margin_top = fields.Float('Date Margin Top', default=0.0)
    date_margin_left = fields.Float('Date Margin Left', default=0.0)
    do_margin_top = fields.Float('DO Margin Top', default=0.0)
    do_margin_left = fields.Float('DO Margin Left', default=0.0)
    lpo_margin_top = fields.Float('LPO Margin Top', default=0.0)
    lpo_margin_left = fields.Float('LPO Margin Left', default=0.0)
    co_margin_top = fields.Float('C/O Margin Top', default=0.0)
    co_margin_left = fields.Float('C/O Margin Left', default=0.0)
    payment_terms_margin_top = fields.Float('Payment Terms Margin Top', default=0.0)
    payment_terms_margin_left = fields.Float('Payment Terms Margin Left', default=0.0)
    ship_to_margin_top = fields.Float('Ship To Margin Top', default=0.0)
    ship_to_margin_left = fields.Float('Ship To Margin Left', default=0.0)
    page_no_margin_top = fields.Float('Page no Margin Top', default=0.0)
    page_no_margin_left = fields.Float('Page no Margin Left', default=0.0)

    #Table
    table_height = fields.Float('Height of table (Unit Of Length)', default=120)
    row_number =  fields.Integer('Number of Rows', default=9)
    sr_width = fields.Float('Sr.', default=0.0)
    sr_padding_right = fields.Float('Sr Padding Right', default=0.0)
    name_width = fields.Float('Name', default=0.0)
    name_padding_left = fields.Float('Name Padding Left', default=0.0)
    qty_width = fields.Float('Qty', default=0.0)
    qty_padding_right = fields.Float('Qty Padding Right', default=0.0)
    rate_excl_width = fields.Float('Rate Excl Tax', default=0.0)
    rate_excl_padding_right = fields.Float('Rate Excl. Padding Right', default=0.0)
    rate_incl_width = fields.Float('Rate Incl Tax', default=0.0)
    rate_incl_padding_right = fields.Float('Rage Incl. Padding Right', default=0.0)
    disc_width = fields.Float('Disc', default=0.0)
    disc_padding_right = fields.Float('Disc. Padding Right', default=0.0)
    taxable_width = fields.Float('Taxable value', default=0.0)
    taxable_padding_right = fields.Float('Taxable Padding Right', default=0.0)
    vat_width = fields.Float('VAT', default=0.0)
    vat_margin_top = fields.Float('Vat Margin Top', default=1)
    vat_margin_right = fields.Float('Vat Margin Right', default='-10')
    vat_amt_width = fields.Float('VAT Amount', default=0.0)
    vat_amt_padding_right = fields.Float('Vat Amount Padding Right', default=0.0)
    net_amount_width = fields.Float('Net Amount', default=0.0)
    net_amount_padding_right = fields.Float('Net Amount Padding Right', default=0.0)

    # Total Rows
    total_exc_tax_padding_right = fields.Float('Total Amt Excl Tax Padding Right', default=0.0)
    total_tax_amt_padding_right = fields.Float('Total Tax Amt Padding Right', default=0.0)
    total_net_amt_padding_right = fields.Float('Total Net Amt Padding Right', default=0.0)

    # Aging Bucket
    bucket_top = fields.Float('Top', default=0.0)
    bucket_right = fields.Float('Right', default=0.0)
    bucket_bottom = fields.Float('Bottom', default=0.0)
    bucket_left = fields.Float('Left', default=0.0)

    # Table Rows
    row_unit = fields.Selection([
        ('px', 'px'),
        ('mm', 'mm'),
        ('em', 'em'),
        ('rem', 'rem'),
        ('cm', 'cm'),
        ('inch', 'inch'),
    ], 'Row Unit', default='mm')
    row_height = fields.Float('Row Height')
    row_name_char_count = fields.Integer('Number of Characters (Name)', default=70)

    @api.model
    def action_create_default_object(self):
        """
        Create a template style if not available
        """
        existing = self.search([
            ('name', '=ilike', 'Default Template')
        ], limit=1)
        vals = {
            'name': 'Default Template',
            'unit': 'mm',
            'sr_width': 10,
            'name_width': 65,
            'qty_width': 15,
            'rate_excl_width': 15,
            'rate_incl_width': 15,
            'disc_width': 13,
            'taxable_width': 18,
            'vat_width': 9,
            'vat_amt_width': 15,
            'net_amount_width': 15
        }
        if not existing:
            existing = self.create(vals)

    @api.constrains('font_weight')
    def _check_font_weight_range(self):
        for record in self:
            if record.font_weight < 500 or record.font_weight > 900:
                raise ValidationError("Font Weight must be between 500 and 900.")
