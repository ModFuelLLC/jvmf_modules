# -*- coding: utf-8 -*-
# Copyright (C) 2017 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class Picking(models.Model):
    _inherit = "stock.picking"

    po_id = fields.Many2one('purchase.order', string='PO #')
    partner_ref = fields.Char(related='po_id.partner_ref', string='Vendor Reference')
