# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

# Copyright (c) 2005-2006 Axelor SARL. (http://www.axelor.com)

import logging
import math
from datetime import datetime, timedelta
from werkzeug import url_encode

from odoo import api, fields, models
from odoo.exceptions import UserError, AccessError, ValidationError
from openerp.tools import float_compare
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.translate import _

_logger = logging.getLogger(__name__)


HOURS_PER_DAY = 8.0

class HolidaysRequest(models.Model):
    _inherit = "hr.leave"

    @api.model
    def _total_leave_hours(self):
        for holiday in self:
            holiday.total_hours = holiday.number_of_days * HOURS_PER_DAY

    payslip_ids = fields.Many2many('hr.payslip', 'hr_payslip_leave_rel', 'leave_id', 'payslip_id', string='Payslips', readonly=True)
    total_hours = fields.Float(string='Total Hours', compute='_total_leave_hours')

    @api.model
    def get_vals(self):
        return {
            'employee_id': self.employee_id.id,
            'holiday_status_id': self.holiday_status_id.id,
            'report_note': self.report_note,
            'holiday_status_id': self.holiday_status_id.id,
            'first_approver_id': self.first_approver_id.id,
            'second_approver_id': self.second_approver_id.id,
            'date_to': self.date_to,
            'date_from': self.date_from,
            'notes': self.notes,
            'category_id': self.category_id.id,
            'number_of_days': self.number_of_days,
            'report_note': self.report_note,
        }

    @api.constrains('payslip_ids')
    def check_for_payslip(self):
        self.payslip_status = False
        if self.payslip_ids:
            self.payslip_status = True

    #Method to split holidays if they cross over the end of the payroll period
    @api.model
    def split_holiday(self):
        #get payroll period from payslip
        pay_period = self.env['hr.payslip'].get_payroll_payperiod()
        #create empty list for new and edited holidays
        new_holidays = self.env['hr.leave']
        #cycle through all holidays
        for holiday in self:
            #retrieve the holiday's date from and date to to check if it crosses over the end of the pay period
            date_from = holiday.date_from
            date_to = holiday.date_to
            if holiday.state == 'validate' and date_from <= pay_period['date_to'] and date_to > pay_period['date_to']:
                #if the holiday crosses over the end of the pay peiod split it
                #retrieve and split number of days
                number_of_days = holiday.number_of_days
                total_length = (date_to - date_from).days + 1.0
                current_length = (pay_period['date_to'] - date_from).days + 1.0
                next_length = total_length - current_length
                actual_days_current = number_of_days * (current_length/total_length)
                actual_days_next = number_of_days - actual_days_current
                #get values from original holiday to create new holiday
                vals = holiday.get_vals()
                #set date from  and number of days for new holiday
                vals['date_from'] = (pay_period['date_to'] + timedelta(days=1)).replace(hour=date_from.hour, minute=date_from.minute, second=date_from.second)
                vals['number_of_days'] = actual_days_next
                vals['name'] = _("%s to %s") % (vals['date_from'].strftime('%Y-%m-%d'), vals['date_to'].strftime('%Y-%m-%d'))
                #update the original holiday with new date to and number of days
                holiday.update({
                    'date_to': pay_period['date_to'],
                    'number_of_days': actual_days_current,
                    'name': _("%s to %s") % (holiday.date_from.strftime('%Y-%m-%d'), pay_period['date_to'].strftime('%Y-%m-%d'))
                })

                #create new holiday
                new_holiday = self.env['hr.leave'].create(vals)
                new_holiday.action_approve()

                #print message in each holiday indicating the split
                message = _("This holiday was split into <a href=# data-oe-model=hr.leave data-oe-id=%d>%s</a> and <a href=# data-oe-model=hr.leave data-oe-id=%d>%s</a>") % (holiday.id, holiday.name, new_holiday.id, new_holiday.name)
                new_message = _("This holiday was split from <a href=# data-oe-model=hr.leave data-oe-id=%d>%s</a>") % (holiday.id, holiday.name)
                holiday.message_post(body=message)
                new_holiday.message_post(body=new_message)

                #put both hoidays into the list of new holidays to return at the end of the method.
                new_holidays |= holiday
                new_holidays |= new_holiday
        return new_holidays
