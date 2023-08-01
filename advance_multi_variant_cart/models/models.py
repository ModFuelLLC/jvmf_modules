# -*- coding: utf-8 -*-

import itertools
import logging

from odoo.addons import decimal_precision as dp

from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError, RedirectWarning, UserError
from odoo.osv import expression
from odoo.tools import pycompat


_logger = logging.getLogger(__name__)


# class Product(models.Model):
#     _inherit = 'product.product'
#
#     saleable_trigger = fields.Boolean('Saleable Trigger', compute='_compute_saleable_qty')
#     saleable_qty = fields.Float('Avalable for Sale',
#         compute='_compute_saleable_qty', store=True,
#         digits=dp.get_precision('Product Unit of Measure'))
#
#     @api.multi
#     def _compute_saleable_qty(self):
#         res = self._compute_quantities_dict(self._context.get('lot_id'), self._context.get('owner_id'), self._context.get('package_id'))
#         _logger.debug('Updating %d products.', len(res))
#         for product in self:
#             product.write({'saleable_qty': res[product.id]['qty_available'] - res[product.id]['outgoing_qty'],})
#             _logger.debug('Updating product: ' + res[product.id])

class ProductTemplate(models.Model):
    _inherit = "product.template"

    # saleable_trigger = fields.Boolean('Saleable Trigger', compute='_compute_saleable_qty')
    # saleable_qty = fields.Float('Avalable for Sale',
    #     compute='_compute_saleable_qty', store=True,
    #     digits=dp.get_precision('Product Unit of Measure'))
    #
    # @api.model
    # def _compute_saleable_qty(self):
    #     res = self._compute_quantities_dict()
    #     for template in self:
    #         template.write({'saleable_qty': res[template.id]['qty_available'] - res[template.id]['outgoing_qty'],})

    @api.multi
    def get_existing_combinations_variants(self):
        self.ensure_one()
        """Get existing combinations.

        Needed because when not using dynamic attributes, the combination is
        not ok if it doesn't exist (= if the variant has been deleted).

        Array, each element is an array with ids of an existing combination.
        """

        valid_value_ids = self._get_valid_product_attribute_values()._without_no_variant_attributes()
        valid_attribute_ids = self._get_valid_product_attributes()._without_no_variant_attributes()

        # Search only among those having the right set of attributes.
        domain = [('product_tmpl_id', '=', self.id), ('active', '=', True)]
        for pa in valid_attribute_ids:
            domain = expression.AND([[('attribute_value_ids.attribute_id.id', '=', pa.id)], domain])
        existing_variants = self.env['product.product'].search(domain)
        own_exclude = self._get_own_attribute_exclusions()
        hidden_variant = []

        existing_variants = existing_variants.filtered(lambda v: v._has_valid_attributes(valid_attribute_ids, valid_value_ids))
        for exist_v in existing_variants:
        	for values in exist_v.attribute_value_ids:
        		if values.id in own_exclude and own_exclude[values.id] and set(own_exclude[values.id]).issubset(set(exist_v.attribute_value_ids.ids))==True:
        			hidden_variant.append(exist_v.id)
        return hidden_variant
