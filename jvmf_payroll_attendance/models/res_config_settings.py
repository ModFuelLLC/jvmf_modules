# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from datetime import datetime, timedelta

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    #Sets the maximum time someone is allowed to be clocked in.
    max_time = fields.Float('Max Time Clocked In', default_model='hr.attendance',
        help="The maximum amount of time someone can be clocked in before the system clocks them out.")

    #sets a default pay period start date, only need to set it once
    pay_period_start_date = fields.Datetime(string="Start of Original Pay Period", default_model='hr.attendance',
        help="A date starting any pay period (doesn't have to be the current pay period)")

    #set hr notification for birthdays, anniversaries, and 90 day reviews
    hr_contact = fields.Many2one('res.users', string='HR Contact', domain=[('share', '=', False)], related='company_id.hr_contact', readonly=False,
        help='The person who gets notified when an employee has a birthday, anniversary, or 90 day review.')


    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        res['max_time'] = float(self.env['ir.config_parameter'].sudo().get_param('attendance.max_time', default=0.0))
        res['pay_period_start_date'] = self.env['ir.config_parameter'].sudo().get_param('payroll.pay_period_start_date', default=False)
        return res

    @api.model
    def set_values(self):
        self.env['ir.config_parameter'].sudo().set_param('attendance.max_time', self.max_time)
        self.env['ir.config_parameter'].sudo().set_param('payroll.pay_period_start_date', self.pay_period_start_date)
        super(ResConfigSettings, self).set_values()
