# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _


class Company(models.Model):
    _inherit = "res.company"

    adp_company_id = fields.Char('ADP Company Code')
    hr_contact = fields.Many2one('res.users', string='HR Contact')
