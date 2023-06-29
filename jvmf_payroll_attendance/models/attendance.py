# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime, timedelta, date
import time
import pytz
import math
from odoo.tools.safe_eval import safe_eval
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT

class HrAttendance(models.Model):
    _inherit = "hr.attendance"

    #set Job Id based on contract
    @api.onchange('contract_id')
    @api.constrains('contract_id')
    def _get_job_id(self):
        for attendance in self:
            if attendance.contract_id:
                attendance.job_id = attendance.contract_id.job_id

    #set timezone sensitive date for filtering and searching
    @api.model
    def _timezone(self):
        a_timezone = self._default_location().location_timezone
        if not a_timezone:
            a_timezone = 'UTC'
        return a_timezone

    #set timezone sensitive date for filtering and searching
    @api.constrains('check_in')
    def _tz_check_in(self):
        for attendance in self:
            tz = pytz.timezone(attendance._timezone())
            checkin = pytz.timezone('UTC').localize(attendance.check_in).astimezone(tz).strftime(DEFAULT_SERVER_DATETIME_FORMAT)
            if not attendance.tz_check_in or attendance.tz_check_in != checkin:
                attendance.write({'tz_check_in': datetime.strptime(checkin, DEFAULT_SERVER_DATETIME_FORMAT)})

    @api.constrains('check_out')
    def _tz_check_out(self):
        for attendance in self:
            tz = pytz.timezone(attendance._timezone())
            if attendance.check_out:
                checkout = pytz.timezone('UTC').localize(attendance.check_out).astimezone(tz).strftime(DEFAULT_SERVER_DATETIME_FORMAT)
                if not attendance.tz_check_out or attendance.tz_check_out != checkout:
                    attendance.write({'tz_check_out': datetime.strptime(checkout, DEFAULT_SERVER_DATETIME_FORMAT)})
            else:
                attendance.write({'tz_check_out': False})


    @api.multi
    def _timezone_check(self):
        attendances = self.env['hr.attendance'].search([('check_in', '>', (datetime.now() - timedelta(weeks=6)).replace(hour=0, minute=0, second=0, microsecond=0).strftime(DEFAULT_SERVER_DATETIME_FORMAT)), ('tz_check_in', '=', False)])
        if attendances:
            for attendance in attendances:
                if attendance.check_in and not attendance.tz_check_in:
                    attendance._tz_check_in()
                if attendance.check_out and not attendance.tz_check_out:
                    attendance._tz_check_out()


    location_id = fields.Many2one('employment.locations')
    zone_id = fields.Many2one('employment.locations', related="location_id.parent_id", store=True, readonly=True)
    contract_id = fields.Many2one('hr.contract', string='Contract')
    job_id = fields.Many2one('hr.job', string='Job Title')
    check_job = fields.Boolean(compute=_get_job_id, default=False)
    company_id = fields.Many2one('res.company', related='contract_id.company_id', string='Company', store=True, readonly=True)
    auto_checkout = fields.Boolean(string='Auto Check Out', default=False)
    overtime_hours = fields.Boolean(string='Over Time', default=False)
    payslip_id = fields.Many2one('hr.payslip', string='Payslip')
    tz_check_in = fields.Datetime(string='check in w/ tz')
    tz_check_out = fields.Datetime(string='check out w/ tz')
    timezone_check = fields.Boolean(compute='_timezone_check')


    # Check all attendances for the previous week and check to see if anyone worked overtime.
    #if so, create new attendances to mark as overtime and mark overtime any attendance after as overtime
    @api.model
    def calculate_overtime(self):
        #Grab today
        today = datetime.today()
        today = today.replace(hour=0, minute=0, second=0, microsecond=0)

        #calculate the week to check for overtime
        week_start = (today - timedelta(days=today.weekday()+1))-timedelta(days=7)
        week_end = week_start + timedelta(days=7)

        #get list of employees that worked during the previous week.
        employees = self.env['hr.attendance'].search([('tz_check_in', '>=', week_start.strftime(DEFAULT_SERVER_DATETIME_FORMAT)),
        ('tz_check_in', '<', week_end.strftime(DEFAULT_SERVER_DATETIME_FORMAT))]).mapped('employee_id')

        #list of attendances to write/create
        new_attendances = self.env['hr.attendance']

        for employee in employees:
            #get list of attendances for the week checked.
            attendances = self.env['hr.attendance'].search([
                ('employee_id', '=', employee.id),
                ('tz_check_in', '>=', week_start.strftime(DEFAULT_SERVER_DATETIME_FORMAT)),
                ('tz_check_in', '<', week_end.strftime(DEFAULT_SERVER_DATETIME_FORMAT))])

            if attendances:
                #calculate the total number of hours worked for the week
                total_worked_hours = math.fsum(attendances.mapped('worked_hours'))

                #Beginning value for standard time hours
                standard_hours = 40

                #check to see if the employee worked over 40 hours in the checked week.
                if total_worked_hours > 40:
                    #cycle through each of the employee's attendances for that week to find when in the week they reached 40 hours
                    for attendance in attendances.sorted(key='check_in'):

                        if attendance.worked_hours <= standard_hours:
                            standard_hours -= attendance.worked_hours
                        #If the employee worked over 40 hours check to see if it happened mid attendance
                        elif attendance.worked_hours > standard_hours:
                            #if an attendance is entirely over time mark as overtime
                            if standard_hours <= 0:
                                attendance.write({
                                    'overtime_hours': True,
                                })
                                new_attendances |= attendance
                            #if overtime happens mid attendance split attendance and mark the overtime hours as overtime.
                            else:
                                check_in = attendance.check_in
                                check_out = attendance.check_out
                                #update the original
                                attendance.write({
                                    'check_out': (check_in + timedelta(hours=standard_hours)).strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                                })

                                new_attendances |= attendance
                                vals = attendance.get_vals()
                                vals['check_in'] = (check_in + timedelta(hours=standard_hours) + timedelta(seconds=1)).strftime(DEFAULT_SERVER_DATETIME_FORMAT)
                                vals['check_out'] = check_out.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
                                vals['overtime_hours'] = True
                                overtime_attendances = self.env['hr.attendance'].create(vals)
                                new_attendances |= overtime_attendances
                                standard_hours = 0.0
        return new_attendances

    #method for cron job that tests and sets for auto clock out.
    @api.multi
    def check_hours_worked(self):
        attendances = self.env['hr.attendance'].search([('check_out', '=', False)])
        settings = self.env['res.config.settings'].get_values()
        max_time = settings['max_time']
        for attendance in attendances:
            check_in = attendance.check_in
            if not attendance.check_out:
                elapsed_time = datetime.now() - check_in
                if  (elapsed_time.total_seconds()/3600.0) >= max_time:
                    attendance.check_out = check_in + timedelta(minutes=1)
                    attendance.auto_checkout = True

    #method for grabbing values from one attendance except for date time information.  Used for splitting attendances.
    @api.model
    def get_vals(self):
        return {
            'employee_id': self.employee_id.id,
            'location_id': self.location_id.id,
            'job_id': self.job_id.id,
            'contract_id': self.contract_id.id,
            'overtime_hours': self.overtime_hours,
            'auto_checkout': self.auto_checkout,
        }

    #return active location
    @api.model
    def _default_location(self):
        non_payroll_locations = self.env['employment.locations'].search([('payroll_location', '=', False)])
        default_location = self.location_id
        if default_location in non_payroll_locations or not default_location:
            default_location = self.employee_id.location_ids.filtered(lambda p: p.primary_location == True).mapped('location_id')
        return default_location

    #Automated method to split the previous days attendances if any of them cross over a date.
    @api.model
    def split_attendance(self):
        #Get attendnaces
        attendances = self.env['hr.attendance'].search([('tz_check_out', '!=', False)]).filtered(lambda r: r.tz_check_in.date() != r.tz_check_out.date())
        attendances |= self.env['hr.attendance'].search([('tz_check_in', '!=', False), ('tz_check_out', '=', False)]).filtered(lambda r: r.tz_check_in.date() != date.today())
        #empty list for new and edited attendances
        new_attendances = self.env['hr.attendance']

        #split attendnaces that do not have the same check in date and check out date
        for attendance in attendances.sorted(key='check_in'):
            tz = pytz.timezone(attendance._timezone())
            check_in = tz.localize(attendance.tz_check_in)
            check_out = tz.localize(attendance.tz_check_out) if attendance.check_out else datetime.now(tz)
            #get values for new attendance
            vals = attendance.get_vals()
            vals['check_in'] = check_out.replace(hour=0, minute=0, second=0).astimezone(pytz.utc)
            if attendance.check_out:
                vals['check_out'] = check_out.astimezone(pytz.utc)

            #update the original attendance with new checkout
            attendance.write({
                'check_out': check_in.replace(hour=23, minute=59, second=59).astimezone(pytz.utc),
            })
            new_attendances |= attendance

            #create new attendance for new day
            new_attendance = self.env['hr.attendance'].create(vals)
            new_attendances |= new_attendance
        return new_attendances
