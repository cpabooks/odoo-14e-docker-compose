from odoo import models, tools, fields, api, _
import logging
from num2words import num2words


class ResCurrency(models.Model):
    _inherit = 'res.currency'

    def amount_to_text(self, amount):
        self.ensure_one()

        # If the currency is INR, use the Indian numbering system
        if self.name == 'INR':
            return self._amount_to_text_indian(amount)

        # Otherwise, call the original method from the parent class
        return super(ResCurrency, self).amount_to_text(amount)


    def _amount_to_text_indian(self, amount):
        """
        Convert the given amount into words using the Indian numbering system.
        E.g., 2,23,634.26 = "Two Lakh Twenty Three Thousand Six Hundred Thirty Four Rupees and Twenty Six Paise"
        """
        units = [
            "", "One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine", "Ten",
            "Eleven", "Twelve", "Thirteen", "Fourteen", "Fifteen", "Sixteen", "Seventeen", "Eighteen", "Nineteen"
        ]
        tens = ["", "", "Twenty", "Thirty", "Forty", "Fifty", "Sixty", "Seventy", "Eighty", "Ninety"]

        def num_to_words(n):
            if n == 0:
                return ""
            elif n < 20:
                return units[n]
            elif n < 100:
                return tens[n // 10] + ('' if n % 10 == 0 else ' ' + units[n % 10])
            else:
                return ""

        # Split the number into integer and fractional parts
        formatted = "%.{0}f".format(self.decimal_places) % amount
        parts = formatted.partition('.')
        integer_value = int(parts[0])
        fractional_value = int(parts[2] or 0)

        num_str = str(integer_value)
        length = len(num_str)
        parts_text = []

        # Process the Crore, Lakh, Thousand, Hundred, and remaining digits
        crore, lakh, thousand, hundred, rest = 0, 0, 0, 0, 0
        if length > 7:
            crore = int(num_str[:-7])
        if length > 5:
            lakh = int(num_str[-7:-5])
        if length > 3:
            thousand = int(num_str[-5:-3])
        if length > 2:
            hundred = int(num_str[-3:-2])
        rest = int(num_str[-2:])

        if crore:
            parts_text.append(num_to_words(crore) + ' Crore')
        if lakh:
            parts_text.append(num_to_words(lakh) + ' Lakh')
        if thousand:
            parts_text.append(num_to_words(thousand) + ' Thousand')
        if hundred:
            parts_text.append(num_to_words(hundred) + ' Hundred')

        # Process the last two digits properly (rest)
        if rest:
            if rest < 20:
                parts_text.append(num_to_words(rest))
            else:
                parts_text.append(tens[rest // 10] + ('' if rest % 10 == 0 else ' ' + units[rest % 10]))

        # Join parts into the final amount in words
        amount_words = ' '.join(parts_text) + " Rupees"

        # Handling fractional part (paise)
        if not self.is_zero(amount - integer_value):
            amount_words += ' ' + _('and') + ' ' + num_to_words(fractional_value) + ' Paise'

        return amount_words
