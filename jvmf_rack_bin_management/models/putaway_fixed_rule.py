# -*- coding: utf-8 -*-
# Copyright (C) 2012 - TODAY, Ursa Information Systems
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockPutawayFixedRule(models.Model):
    _name = 'stock.putaway.fixed.rule'
    _description = "Putaway strategy with fixed location per warehouse"

    name = fields.Many2one('product.product', string="Product",
                           domain=[('type', 'in', ('product', 'consu'))])
    warehouse_id = fields.Many2one('stock.warehouse', string="Warehouse")
    rack = fields.Char('Rack', size=16)
    shelf = fields.Char('Shelf', size=16)
    bin = fields.Char('Bin', size=16)
    company_id = fields.Many2one("res.company",
                                 related="warehouse_id.company_id",
                                 store="True",
                                 readonly="True",
                                 string="Company")
    alt_location_id = fields.Many2one('stock.location',
                                      string='Alt Location',
                                      domain=[('usage', '=', 'internal')])

    _sql_constraints = [
        ('stock_putaway_fixed_rule_uniq',
         'unique(name,warehouse_id)',
         'There is already a rule for this product in the same warehouse!')
    ]
