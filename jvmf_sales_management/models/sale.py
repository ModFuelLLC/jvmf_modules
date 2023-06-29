# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class SaleOrder(models.Model):
    _inherit = "sale.order"

    partner_ref = fields.Char('Vendor Reference')

    #Auto sets the sales team based on the salesperson
    @api.onchange('user_id')
    def _sales_team(self):
        self.team_id = ''
        if self.user_id.sale_team_id:
            self.team_id = self.user_id.sale_team_id

    def _get_delivery_methods(self):
        res = super(SaleOrder, self)._get_delivery_methods()
        res |= self.partner_shipping_id.property_delivery_carrier_id
        return res
