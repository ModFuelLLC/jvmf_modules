# -*- coding: utf-8 -*-
# Copyright (C) 2017 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
import odoo.addons.decimal_precision as dp

class CustomerProductReturn(models.Model):
    _inherit = "product.return"
    #add incoming carrier information
    incoming_carrier_id = fields.Many2one('delivery.carrier', string='Carrier')
    incoming_carrier_tracking_ref = fields.Char(string='Tracking Reference', copy=False)
