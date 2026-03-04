from odoo import models, fields, api


class WeekDay(models.Model):
    _name = 'week.day'

    name=fields.Char(string="Week Day")


# class WeekDay(models.Model):
#     _name = 'week.day'
#
#     name=fields.Char(string="Week Day")