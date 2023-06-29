#-*- coding:utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import time
from datetime import datetime, timedelta
from dateutil import relativedelta

import babel

from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT

from odoo.addons import decimal_precision as dp


class HrPayslipValidate(models.Model):
    _name = 'hr.payslip.validate'

    payslip_id = fields.Many2one('hr.payslip', string='Related Payslip', readonly=True)
    user_id = fields.Many2one('res.users', string='Verifying User', readonly=True)
    date_validated = fields.Datetime(string='Verification Timestamp', readonly=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('verify', 'Waiting'),
        ('confirm','Confirmed'),
        ('done', 'Done'),
        ('cancel', 'Rejected'),
    ], string='Verification Status', index=True, readonly=True, copy=False, default='draft',
        help="""* When the payslip is created the status is \'Draft\'
                \n* If the payslip is under verification, the status is \'Waiting\'.
                \n* If the payslip is confirmed then status is set to \'Done\'.
                \n* When user cancel payslip the status is \'Rejected\'.""")
