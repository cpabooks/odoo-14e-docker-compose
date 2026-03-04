from email.policy import default

from pkg_resources import require

from odoo import api, models, fields, _

class VatSummaryReport(models.Model):
    _name = 'vat.summary.report'
    _description = 'Vat Summary Report'

    name = fields.Char('Name')
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True)
    report_ids = fields.One2many('vat.summary.report.line', 'vat_id', 'Statutory')
    summary_year_id = fields.Many2one('vat.summary.year', 'Summary')

    @api.model
    def create(self, vals):
        res = super(VatSummaryReport, self).create(vals)
        if res.summary_year_id:
            self.env['vat.summary.year.line'].create({
                'summary_id': res.id,
                'year_id': res.summary_year_id.id,
            })
        return res

    @api.model
    def default_get(self, fields_list):
        res = super(VatSummaryReport, self).default_get(fields_list)
        res.update({
            'company_id': self.env.company.id
        })
        return res


    def write(self, vals):
        res = super(VatSummaryReport, self).write(vals)
        if 'summary_year_id' in vals and self.summary_year_id:
            self.env['vat.summary.year.line'].create({
                'summary_id': self.id,
                'year_id': self.summary_year_id.id,
            })
        return res

    def _create_summary_year(self):
        summary_year = self.env['vat.summary.year']
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

    def action_create_summary_data(self):
        self._create_summary_year()
        company_ids = self.env['res.company'].search([])
        for company in company_ids:
            for year in range(2018, 2016):
                summary_name = f'VAT Summary {year}'
                summary_year = self.env['vat.summary.year'].search([
                    ('name', '=ilike', summary_name),
                    ('company_id', '=', company.id)
                ], limit=1)
                if summary_year:
                    for q in range(1, 5):
                        name = f'VAT Summary Q{q}/{year}'
                        search_self = self.search([
                            ('name', '=ilike', name),
                            ('company_id', '=', company.id)
                        ], limit=1)
                        if not search_self:
                            summary_report = self.create({
                                'name': name,
                                'summary_year_id': summary_year.id,
                                'company_id': company.id
                            })
                            print(f'Created summary report for {summary_report.name}')


class VatSummaryReportLine(models.Model):
    _name = 'vat.summary.report.line'
    _description = 'Vat Summary Report Line'

    vat_id = fields.Many2one('vat.summary.report', 'VAT Summary')
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True)
    sr_no = fields.Integer('Sr No.', default=0, compute='_get_line_numbers')
    period_start = fields.Date('Period Start', default=fields.Date.today)
    period_end = fields.Date('Period End')
    sales = fields.Float('Sales')
    sale_tax = fields.Float('Tax', compute='_compute_tax')
    purchase = fields.Float('Purchase')
    purchase_tax = fields.Float('Tax', compute='_compute_tax')
    net_vat_position = fields.Float('Net VAT Position', compute = '_compute_net_vat')

    @api.model
    def default_get(self, fields_list):
        res = super(VatSummaryReportLine, self).default_get(fields_list)
        res.update({
            'company_id': self.env.company.id
        })
        return res


    @api.depends('sales', 'purchase')
    def _compute_tax(self):
        """Compute taxes with 5% of sales and purchase"""
        for rec in self:
            if rec.sales:
                rec.sale_tax = (rec.sales * 5) / 100
            else:
                rec.sale_tax = 0.0
            if rec.purchase:
                rec.purchase_tax = (rec.purchase * 5) / 100
            else:
                rec.purchase_tax = 0.0

    @api.depends('sale_tax', 'purchase_tax')
    def _compute_net_vat(self):
        """Calculate net_vat_position = sale_tax - purchase_tax"""
        for rec in self:
            rec.net_vat_position = rec.sale_tax - rec.purchase_tax

    def _get_line_numbers(self):
        for rec in self:
            line_num = 1
            if rec.ids:
                first_line_rec = self.browse(rec.ids[0])

                for line_rec in first_line_rec.vat_id.report_ids:
                    line_rec.sr_no = line_num
                    line_num += 1


