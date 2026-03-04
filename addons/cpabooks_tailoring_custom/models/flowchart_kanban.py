# -*- coding: utf-8 -*-

from odoo import models, fields


class FlowchartTrailorKanban(models.Model):
    _name = 'flowchart.tailor.kanban'
    _description = 'Flowchart Tailor Kanban'

    name = fields.Char(string='Name')

    def action_stock_picking_incoming(self):
        action = self.env.ref('stock.stock_picking_action_picking_type').read()[0]
        action['domain'] = [('picking_type_code', '=', 'incoming')]
        return action

    def action_stock_picking_outgoing(self):
        action = self.env.ref('stock.stock_picking_action_picking_type').read()[0]
        action['domain'] = [('picking_type_code', '=', 'outgoing')]
        return action
