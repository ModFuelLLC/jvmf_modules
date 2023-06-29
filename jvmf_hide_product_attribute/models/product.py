# -*- coding: utf-8 -*-
# Copyright (C) 2017 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _


class ProductAttributes(models.Model):
    _inherit = "product.attribute"

    hide_on_website = fields.Boolean(string='Hide On Website',default=False)

"""
class ProductAttributeValue(models.Model):
    _inherit = "product.attribute.value"

    hide_on_website = fields.Boolean(string='Hide On Website',default=False)
"""
