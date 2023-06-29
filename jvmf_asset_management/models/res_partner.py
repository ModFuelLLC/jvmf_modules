# coding: utf-8

from odoo import api, fields, models

class ResPartner(models.Model):
    _inherit = 'res.partner'


    asset_loan_allowed = fields.Boolean(string='Can Borrow Assets')
    loaned_assets = fields.One2many('asset.loan.line', 'partner_id', string="Assets on loan", domain=[('state','in',['needs_approval','approved','checked_out','over_due'])], readonly=True)
