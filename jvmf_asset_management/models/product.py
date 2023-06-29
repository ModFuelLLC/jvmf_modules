# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError
from odoo.osv import expression
from odoo.addons import decimal_precision as dp
from odoo.tools import float_compare, pycompat


class ProductTemplate(models.Model):
    _inherit = "product.template"

    def _compute_assets(self):
        for product in self:
            product.asset_count = len(product.asset_ids)
    def _compute_assets_available(self):
        for product in self:
            product.asset_available_count = len(product.asset_ids.filtered(lambda self: self.loan_availability == 'in'))

    asset_ids = fields.One2many('account.asset.asset', 'product_id', string='Assets')
    asset_count = fields.Integer(string='Number of Assets', compute='_compute_assets')
    asset_available_count = fields.Integer(string='Number of Assets Available', compute='_compute_assets_available')
    asset_loan_ok = fields.Boolean(string='Can be Loaned')

    #define button for viewing assets
    @api.multi
    def action_view_assets(self):
        action = self.env.ref('account_asset.action_account_asset_asset_form').read()[0]
        assets = self.mapped('asset_ids')
        if len(assets) > 1:
            action['domain'] = [('id', 'in', assets.ids)]
        elif assets:
            action['views'] = [(self.env.ref('account_asset.view_account_asset_asset_form').id, 'form')]
            action['res_id'] = assets.id
        return action
