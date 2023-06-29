# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    minimum_check_number = fields.Integer(string='Minimum Check #', help='Used to manually control the check number sequencing.')
