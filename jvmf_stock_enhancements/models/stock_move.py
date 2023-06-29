# -*- coding: utf-8 -*-

from odoo import api, exceptions, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import float_compare, float_round
from odoo.addons import decimal_precision as dp


class StockMove(models.Model):
    _inherit = 'stock.move'


    @api.multi
    def split_move_lot(self):
        ctx = dict(self.env.context)
        self.ensure_one()
        view = self.env.ref('mrp.view_stock_move_lots')
        serial = (self.has_tracking == 'serial')
        only_create = False  # Check picking type in theory
        show_reserved = any([x for x in self.move_line_ids if x.product_qty > 0.0])
        ctx.update({
            'serial': serial,
            'only_create': only_create,
            'create_lots': True,
            'state_done': self.is_done,
            'show_reserved': show_reserved,
        })
        if ctx.get('w_production'):
            action = self.env.ref('mrp.act_mrp_product_produce').read()[0]
            action['context'] = ctx
            return action
        result = {
            'name': _('Register Lots'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'stock.move',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new',
            'res_id': self.id,
            'context': ctx,
        }
        return result
