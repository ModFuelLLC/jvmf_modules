# coding: utf-8

from odoo import api, fields, models
from odoo.addons import decimal_precision as dp


class Product(models.Model):
    _inherit = 'product.product'

    saleable_trigger = fields.Boolean('Saleable Trigger', compute='_compute_saleable_qty')
    saleable_qty = fields.Float('Avalable for Sale',
        compute='_compute_saleable_qty', store=True,
        digits=dp.get_precision('Product Unit of Measure'))

    @api.multi
    def _compute_saleable_qty(self):
        # import pdb; pdb.set_trace()
        res = self._compute_quantities_dict(self._context.get('lot_id'), self._context.get('owner_id'), self._context.get('package_id'))
        for product in self:
            product.write({'saleable_qty': res[product.id]['qty_available'] - res[product.id]['outgoing_qty'],})


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    saleable_trigger = fields.Boolean('Saleable Trigger', compute='_compute_saleable_qty')
    saleable_qty = fields.Float('Avalable for Sale',
        compute='_compute_saleable_qty', store=True,
        digits=dp.get_precision('Product Unit of Measure'))

    @api.model
    def _compute_saleable_qty(self):
        res = self._compute_quantities_dict()
        for template in self:
            template.write({'saleable_qty': res[template.id]['qty_available'] - res[template.id]['outgoing_qty'],})
