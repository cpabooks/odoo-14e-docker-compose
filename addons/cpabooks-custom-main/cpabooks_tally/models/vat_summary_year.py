from odoo import api, models, fields, _

class VATSummaryYear(models.Model):
    _name = 'vat.summary.year'
    _description = 'Vat Summary By Year'
    _rec_name = 'name'



    name = fields.Char('Name')
    company_id = fields.Many2one('res.company', 'Company', )
    summary_line = fields.One2many('vat.summary.year.line', 'year_id', 'Summary')

    sales = fields.Float('Sales', compute='_compute_total_sales_purchase')
    sale_tax = fields.Float('Tax', compute='_compute_tax')
    purchase = fields.Float('Purchase', compute='_compute_total_sales_purchase')
    purchase_tax = fields.Float('Tax', compute='_compute_tax')
    net_vat_position = fields.Float('Net VAT Position', compute='_compute_net_vat')

    @api.model
    def default_get(self, fields_list):
        res = super(VATSummaryYear, self).default_get(fields_list)
        res.update({
            'company_id': self.env.company.id
        })
        return res

    def _compute_total_sales_purchase(self):
        for rec in self:
            sale_total = sum(rec.summary_line.mapped('sales'))
            purchase_total = sum(rec.summary_line.mapped('purchase'))

            rec.sales = sale_total
            rec.purchase = purchase_total

    @api.depends('sales', 'purchase')
    def _compute_tax(self):
        """Compute taxes with 5% of sales and purchase"""
        for rec in self:
            rec.sale_tax = (rec.sales * 5) / 100 if rec.sales else 0.0
            rec.purchase_tax = (rec.purchase * 5) / 100 if rec.purchase else 0.0

    @api.depends('sale_tax', 'purchase_tax')
    def _compute_net_vat(self):
        """Calculate net_vat_position = sale_tax - purchase_tax"""
        for rec in self:
            rec.net_vat_position = rec.sale_tax - rec.purchase_tax

    def _create_summary_line(self, summary_year_id=False, year=False, company=False):
        summary_line = self.env['vat.summary.year.line']
        if summary_year_id:
            for q in range(1, 5):
                summary_line_name = f'VAT Summary Q{q}/{year}'
                summary_existence = summary_line.search([
                    ('year_id', '=', summary_year_id.id),
                    ('name', '=ilike', summary_line_name),
                    ('company_id', '=', company.id)
                ], limit=1)
                summary_line_vals = {
                    'name': summary_line_name,
                    'year_id': summary_year_id.id,
                }
                if not summary_existence:
                    summary_line_id = summary_line.create(summary_line_vals)
                    print(f'Created summary line named {summary_line_id.name}')


    def _create_summary_year(self):
        summary_year = self.env['vat.summary.year']
        summary_line = self.env['vat.summary.year.line']
        company_ids = self.env['res.company'].search([])
        if company_ids:
            for company in company_ids:
                for year in range(2018, 2026):
                    name = f'VAT Summary {year}'
                    check_existing = summary_year.search([
                        ('name', '=ilike', name),
                        ('company_id', '=', company.id)
                    ], limit=1)
                    if not check_existing:
                        summary_year_id = summary_year.create({
                            'name': name,
                            'company_id': company.id
                        })
                        print(f'Created Summary year for {summary_year_id.name}')
                        self._create_summary_line(summary_year_id=summary_year_id,year=year,company=company)
                    elif check_existing:
                        self._create_summary_line(summary_year_id=check_existing, year=year, company=company)
                        print(f'Updated Summary year for {check_existing.name}')

    @api.model
    def action_create_summary_data(self):
        self._create_summary_year()

class VATSummaryYearLine(models.Model):
    _name = 'vat.summary.year.line'
    _description = 'VAT Summary by Year Line'

    year_id = fields.Many2one('vat.summary.year', 'VAT Summary')
    company_id = fields.Many2one('res.company', 'Company')
    sr_no = fields.Integer('Sr No.', default=0, compute='_get_line_numbers', store=True)
    name = fields.Char('Period')
    date_start = fields.Date('Start Date')
    date_end = fields.Date('End Date')
    # summary_id = fields.Many2one('vat.summary.report', 'Summary Quarter')

    sales = fields.Float('Sales')
    sale_tax = fields.Float('Tax', compute='_compute_tax')
    purchase = fields.Float('Purchase')
    purchase_tax = fields.Float('Tax', compute='_compute_tax')
    net_vat_position = fields.Float('Net VAT Position', compute='_compute_net_vat')

    @api.model
    def default_get(self, fields_list):
        res = super(VATSummaryYearLine, self).default_get(fields_list)
        res.update({
            'company_id': self.env.company.id
        })
        return res

    @api.depends('sales', 'purchase')
    def _compute_tax(self):
        """Compute taxes with 5% of sales and purchase"""
        for rec in self:
            rec.sale_tax = (rec.sales * 5) / 100 if rec.sales else 0.0
            rec.purchase_tax = (rec.purchase * 5) / 100 if rec.purchase else 0.0

    @api.depends('sale_tax', 'purchase_tax')
    def _compute_net_vat(self):
        """Calculate net_vat_position = sale_tax - purchase_tax"""
        for rec in self:
            rec.net_vat_position = rec.sale_tax - rec.purchase_tax

    @api.depends('year_id')
    def _get_line_numbers(self):
        """Assign serial numbers based on sequence"""
        for rec in self:
            if rec.year_id:
                for index, line in enumerate(rec.year_id.summary_line, start=1):
                    line.sr_no = index
