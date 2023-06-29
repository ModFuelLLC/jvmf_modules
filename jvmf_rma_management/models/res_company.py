# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import base64
import os
import re

from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError, UserError


class Company(models.Model):
    _inherit = "res.company"

    rma_followup_contact = fields.Many2one('res.users', string='RMA Followup Contact')
    rma_seq_abbr = fields.Char(string='Sequence Abbreviation')
