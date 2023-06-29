# -*- coding: utf-8 -*-
# Copyright (C) 2012 - TODAY, Ursa Information Systems
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class StockMove(models.Model):
    _inherit = "stock.move"
    _order = "rack,shelf,bin,product_id"

    @api.depends('product_id', 'picking_id.picking_type_id.warehouse_id')
    def _compute_location(self):
        for record in self:
            if record.product_id and\
                    record.picking_id.picking_type_id.warehouse_id:
                rule = self.env['stock.putaway.fixed.rule'].\
                    search([('name', '=', record.product_id.id),
                            ('warehouse_id', '=',
                             record.picking_id.picking_type_id.warehouse_id.id)])
                if rule:
                    record.rack = rule.rack
                    record.shelf = rule.shelf
                    record.bin = rule.bin
                    record.alt_location_id = rule.alt_location_id.id

    alt_location_id = fields.Many2one("stock.location",
                                      compute="_compute_location",
                                      string="Alt Location",
                                      store=True)
    rack = fields.Char("Rack",
                       compute="_compute_location",
                       store=True)
    shelf = fields.Char("Shelf",
                        compute="_compute_location",
                        store=True)
    bin = fields.Char("Bin",
                      compute="_compute_location",
                      store=True)


class StockPackOperation(models.Model):
    _inherit = 'stock.move.line'
    _order = "rack,shelf,bin,product_id"

    @api.depends('product_id', 'picking_id.picking_type_id.warehouse_id')
    def _compute_location(self):
        for record in self:
            if record.product_id and\
                    record.picking_id.picking_type_id.warehouse_id:
                rule = self.env['stock.putaway.fixed.rule'].\
                    search([('name', '=', record.product_id.id),
                            ('warehouse_id', '=',
                             record.picking_id.picking_type_id.warehouse_id.id)])
                if rule:
                    record.rack = rule.rack
                    record.shelf = rule.shelf
                    record.bin = rule.bin
                    record.alt_location_id = rule.alt_location_id.id

    alt_location_id = fields.Many2one("stock.location",
                                      compute="_compute_location",
                                      string="Alt Location",
                                      store=True)
    rack = fields.Char("Rack",
                       compute="_compute_location",
                       store=True)
    shelf = fields.Char("Shelf",
                        compute="_compute_location",
                        store=True)
    bin = fields.Char("Bin",
                      compute="_compute_location",
                      store=True)
