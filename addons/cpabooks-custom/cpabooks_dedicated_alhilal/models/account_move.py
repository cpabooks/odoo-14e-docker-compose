from odoo import api, models, fields, _


class AccountMove(models.Model):
    _inherit = 'account.move'

    is_show_receiver = fields.Boolean('Show Receiver Info')
    supply_date_start = fields.Date('Supply Date Start')
    supply_date_end = fields.Date('Supply Date End')
    psf = fields.Char('PSF', compute='action_psf')

    @api.depends('project_id')
    def action_psf(self):
        for rec in self:
            psf = ''
            if rec.project_id:
                psf = ''.join([word[0].upper() for word in rec.project_id.name.split() if word])
            rec.psf = psf

    @api.model
    def default_get(self, fields):
        res = super(AccountMove, self).default_get(fields)
        get_last_inv = self.env['account.move'].search([
            ('move_type', '=', 'out_invoice')
        ], limit=1, order="id desc")

        if get_last_inv:
            res.update({
                'is_show_receiver': get_last_inv.is_show_receiver
            })
        return res

    @api.onchange('partner_id')
    def get_previous_balance(self):
        for rec in self:
            if rec.partner_id:
                account_ids = self.env['account.account'].search([
                    ('user_type_id.name', 'in', ('Receivable', 'Payable'))
                ])
                lines = self.env['account.move.line'].search([
                    ('partner_id', '=', rec.partner_id.id),
                    ('account_id', 'in', account_ids.ids)
                ])
                if lines:
                    rec.previous_balance = sum(lines.mapped('balance'))
                else:
                    rec.previous_balance = 0.0

    @api.onchange('partner_id')
    def get_previous_balance(self):
        for rec in self:
            if rec.partner_id:
                account_ids = self.env['account.account'].search([
                    ('user_type_id.name', 'in', ('Receivable', 'Payable'))
                ])
                lines = self.env['account.move.line'].search([
                    ('partner_id', '=', rec.partner_id.id),
                    ('account_id', 'in', account_ids.ids)
                ])
                if lines:
                    rec.previous_balance = sum(lines.mapped('balance'))
                else:
                    rec.previous_balance = 0.0

    def action_create_payment_certificate(self):
        vals = {}
        invoice_names = []
        invoice_ids = []

        for rec in self:
            invoice_names.append(rec.name)
            # Correct the way invoice_ids are passed to the wizard
            invoice_ids.append(rec.id)  # Append the record ID, not the record itself

        vals.update({
            'memo': ', '.join(invoice_names),
            'invoice_ids': [(6, 0, invoice_ids)]  # Use the correct format for many2many field
        })

        wizard = self.env['payment.certificate.wizard'].create(vals)
        return {
            'name': 'Create Payment Certificate',
            'type': 'ir.actions.act_window',
            'res_model': 'payment.certificate.wizard',
            'view_mode': 'form',
            'target': 'new',
            'views': [(self.env.ref('cpabooks_dedicated_alhilal.payment_certificate_wizard_form_view').id, 'form')],
            'res_id': wizard.id,  # Corrected: Open the specific created record
        }


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    psf = fields.Char('Project Short Form', compute='_compute_psf')

    @api.depends('analytic_account_id')
    def _compute_psf(self):
        for rec in self:
            short_name = ''
            if rec.analytic_account_id:
                special_chars = [
                    '!', '"', '#', '$', '%', '&', "'", '(', ')', '*', '+', ',', '-', '.', '/',
                    ':', ';', '<', '=', '>', '?', '@', '[', '\\', ']', '^', '_', '`',
                    '{', '|', '}', '~',

                    # Whitespace and control characters
                    ' ', '\t', '\n', '\r',

                    # Currency symbols
                    '¢', '£', '¤', '¥', '₹', '€',

                    # Math symbols
                    '±', '∑', '∞', '≠', '√', '∫', '∆', '∇', '≈', '≥', '≤', '∂', '∏', '∩', '∪', '∈', '∉', '⊂', '⊃', '∅',
                    '∧', '∨', '∀', '∃',

                    # Typographic punctuation
                    '“', '”', '‘', '’', '…', '—', '–', '•', '·',

                    # Miscellaneous symbols
                    '©', '®', '™', '§', '¶', '†', '‡', '‰', '′', '″', '°', 'µ',

                    # Box drawing and block elements
                    '┌', '┐', '└', '┘', '─', '│', '┼', '█', '▓', '▒', '░', '▀', '▄', '▌', '▐',

                    # Arrows and directional symbols
                    '←', '↑', '→', '↓', '↔', '↕', '⇐', '⇒', '⇑', '⇓',

                    # Emojis (a small sample)
                    '😀', '😃', '😄', '😁', '😂', '😅', '😆', '😉', '😊', '😎',
                    '❤️', '💔', '💯', '✔️', '✖️', '⭐', '🔥', '🎉'
                ]
                short_name = ''.join([word[0].upper() for word in rec.analytic_account_id.name.split() if word and word[0] not in special_chars])
            rec.psf = short_name