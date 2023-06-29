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


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    #Gather the appropriate adp information for the payslip
    @api.onchange('contract_id', 'employee_id')
    def _get_adp_ids(self):
        for payslip in self:
            if payslip.employee_id.company_id.name == 'Joost Vapor LLC':
                payslip.adp_employee_id = payslip.employee_id.adp_joost_employee_id
                payslip.adp_location_id = payslip.location_id.adp_joost_location_id
            elif payslip.company_id.name == 'Mod Fuel LLC':
                payslip.adp_employee_id = payslip.employee_id.adp_modfuel_employee_id
                payslip.adp_location_id = payslip.location_id.adp_modfuel_location_id

    #Get the number of attendances for the payslip
    @api.multi
    def _attendance_count(self):
        for payslip in self:
            payslip.attendance_count = len(payslip.attendance_ids)

    #get the adp_department(contract) information
    @api.model
    def _get_adp_department_id(self):
        for payslip in self:
            if payslip.contract_company_id.name == 'Joost Vapor LLC':
                payslip.adp_contract_id = payslip.contract_id.adp_joost_department_id.id
            if payslip.contract_company_id.name == 'Mod Fuel LLC':
                payslip.adp_contract_id = payslip.contract_id.adp_modfuel_department_id.id

    #get the number holidays for this payslip
    @api.multi
    def _holiday_count(self):
        for payslip in self:
            payslip.holiday_count = len(payslip.leave_ids)

    @api.model
    def _total_worked_hours(self):
        for payslip in self:
            for worked_day in payslip.worked_days_line_ids:
                payslip.total_hours_worked += worked_day.number_of_hours

    #calculate total worked hours for the payslip
    @api.onchange('overtime_approved')
    @api.depends('overtime_approved')
    def _total_overtime_hours(self):
        for payslip in self:
            if payslip.overtime_approved:
                for worked_day in payslip.worked_days_line_ids:
                    payslip.total_overtime_hours += worked_day.overtime
            else:
                payslip.total_overtime_hours = 0
        return

    #get contract company information if there is a contract assigned to the payslip
    @api.onchange('contract_id')
    @api.constrains('contract_id')
    def _company_get(self):
        for payslip in self:
            if payslip.contract_id.company_id.name != 'Joost Corp':
                payslip.contract_company_id = payslip.contract_id.company_id
                payslip.company_id = payslip.contract_id.company_id
            else:
                payslip.contract_company_id = payslip.company_id

    @api.constrains('worked_days_line_ids')
    def _has_overtime(self):
        over_time = False
        for worked_day in self.worked_days_line_ids:
            if worked_day.overtime and not over_time:
                over_time = True
        self.has_overtime = over_time

    contract_company_id = fields.Many2one('res.company', string='Company', readonly=True, default=_company_get, store=True)
    location_id = fields.Many2one('employment.locations', string="Location")
    adp_location_id = fields.Char(string='ADP Location ID', compute='_get_adp_ids', store=True, readonly=True)
    adp_company_id = fields.Char(string='CO Code', related='contract_company_id.adp_company_id', readonly=True)
    adp_employee_id = fields.Char(string='File #', compute='_get_adp_ids', store=True, readonly=True)
    adp_contract_id = fields.Char(string='ADP Contract ID', compute='_get_adp_department_id', store=True, readonly=True)
    attendance_ids = fields.One2many('hr.attendance', 'payslip_id', string='Attendances')
    attendance_count = fields.Integer(string='Number of attendances on this pay slip', compute='_attendance_count')
    total_hours_worked = fields.Float(string='Reg Hours', compute='_total_worked_hours', digits=(16, 3))
    total_overtime_hours = fields.Float(string='O/T Hours', compute='_total_overtime_hours', digits=(16, 3))
    leave_ids = fields.Many2many('hr.leave', 'hr_payslip_leave_rel', 'payslip_id', 'leave_id', string='Holidays')
    holiday_count = fields.Integer(string='Number of holidays on this pay slip', compute='_holiday_count')
    job_id = fields.Many2one('hr.job', 'Position', related='contract_id.job_id', store=True, readonly=True)
    has_overtime = fields.Boolean(string='Has Overtime', default=False)
    pay_no = fields.Integer(string='Pay #', default=1)
    batch_no = fields.Char(string='Batch ID', readonly=1)
    cancel_pay = fields.Char(string='Cancel Pay')
    tax_frequency = fields.Char(string='Tax Frequency')
    overtime_approved = fields.Boolean(string='Overtime Approved', default=False, states={'done': [('readonly', True)], 'cancel': [('readonly', True)], 'confirm': [('readonly', True)]})
    validation_ids = fields.One2many('hr.payslip.validate', 'payslip_id', string='Validators', readonly=True)
    state = fields.Selection(selection_add=[('confirm','Confirmed')],
        help="""* When the payslip is created the status is \'Draft\'
                \n* If the payslip is under verification, the status is \'Waiting\'.
                \n* If the payslip is waiting to be exported the status is \'Confirmed\'
                \n* If the payslip has been exported then status is set to \'Done\'.
                \n* When user cancel payslip the status is \'Rejected\'.""")

    @api.multi
    def write(self, vals):
        if not self.batch_no:
            vals['batch_no'] = self.create_date.strftime('%m%d%Y')
        vals['name'] = self.get_payslip_name()
        return super(HrPayslip, self).write(vals)

    #set payslip name based on sequence and company
    @api.model
    def get_payslip_name(self):
        prefix = ''
        if self.contract_company_id.name == 'Joost Vapor LLC':
            prefix = 'JV-'
        elif self.contract_company_id.name == 'Mod Fuel LLC':
            prefix = 'MF-'
        seq = str(self.id).zfill(6)
        return _('%sPay#%s') % (prefix, seq)

    #Method to create and set verifier of payslip
    @api.model
    def create_verifier(self):
        vals = {
            'payslip_id': self.id,
            'user_id': self.env.uid,
            'date_validated': datetime.now(),
            'state': self.state,
        }
        self.env['hr.payslip.validate'].create(vals)

    #Methods to track creation and verification steps
    @api.model
    def create(self, vals):
        if 'batch_no' not in vals:
            vals['batch_no'] = datetime.now().strftime('%m%d%Y')
        res = super(HrPayslip, self).create(vals)
        res.create_verifier()
        val = {'name': res.get_payslip_name()}
        res.write(val)
        return res

    @api.multi
    def action_verify(self):
        self.write({'state': 'verify'})
        self.create_verifier()
        return

    @api.multi
    def check_ot_approved(self):
        if self.has_overtime and not self.overtime_approved:
            view_id = self.env.ref('jvmf_payroll_attendance.verify_overtime').id
            return {
                'name': 'Verify Overtime',
                'type': 'ir.actions.act_window',
                'res_model': 'hr.payslip',
                'res_id': self.id,
                'view_type': 'form',
                'view_mode': 'form',
                'target': 'new',
                'view_id': view_id,
            }
        else:
            self.action_confirm()
            return True

    @api.multi
    def action_approve_overtime(self):
        self.overtime_approved = True
        self.action_confirm()
        return

    @api.multi
    def action_confirm(self):
        self.write({'state': 'confirm'})
        self.create_verifier()
        return

    @api.multi
    def action_payslip_draft(self):
        res = super(HrPayslip, self).action_payslip_draft()
        self.create_verifier()
        return res

    @api.multi
    def action_payslip_cancel(self):
        res = super(HrPayslip, self).action_payslip_cancel()
        self.create_verifier()
        return res

    @api.multi
    def action_payslip_done(self):
        res = super(HrPayslip, self).action_payslip_done()
        self.create_verifier()
        return res

    #obtain the payroll period
    @api.model
    def get_payroll_payperiod(self):
        today = datetime.today()
        today = today.replace(hour=0, minute=0, second=0, microsecond=0)

        #initialize the beginning of the pay period to the beginning of the current week.
        current_start_date = (today - timedelta(days=today.weekday()+1)).replace(hour=0, minute=0, second=0, microsecond=0)

        #Set default original pay period beginning
        original_pay_period_start_date = datetime(2018,7,8)
        #check to see if a new pay period beginning has been set in configs.
        settings = self.env['res.config.settings'].get_values()
        if settings['pay_period_start_date']:
            original_pay_period_start_date = datetime.strptime(settings['pay_period_start_date'], DEFAULT_SERVER_DATETIME_FORMAT)

        #set the start of the current pay period
        if (((current_start_date - original_pay_period_start_date).days/7)%2) != 0:
            current_start_date = current_start_date - timedelta(weeks=1)


        date_from = current_start_date - timedelta(weeks=2)
        date_to = (current_start_date - timedelta(days=1)).replace(hour=23, minute=59, second=59)
        return {
            'date_from': date_from,
            'date_to': date_to,
        }

    #set default pay period on payslip
    @api.model
    def get_date_from(self):
        pay_period = self.get_payroll_payperiod()
        date_from = pay_period['date_from'].strftime('%Y-%m-%d')
        return date_from

    @api.model
    def get_date_to(self):
        pay_period = self.get_payroll_payperiod()
        date_to = pay_period['date_to'].strftime('%Y-%m-%d')
        return date_to

    date_from = fields.Date(string='Date From', readonly=True, required=True, default=get_date_from, states={'draft': [('readonly', False)]})
    date_to = fields.Date(string='Date To', readonly=True, required=True, default=get_date_to, states={'draft': [('readonly', False)]})

    @api.model
    def create_new_payslip(self,employee, contract, company, active_location, pay_period):
        #get vals and create new payslip based off of attendance
        vals = {
            'employee_id': employee.id,
            'contract_id': contract.id,
            'company_id': company,
            'location_id': active_location.id,
            'date_from': pay_period['date_from'],
            'date_to': pay_period['date_to'],
            'state': 'draft',
        }
        #create payslip
        return self.env['hr.payslip'].create(vals)


    #Automated method to create payslips
    @api.model
    def process_payroll(self):
        #get payroll period
        pay_period = self.get_payroll_payperiod()
        total_payslips = self.env['hr.payslip']
        worked_days = self.env['hr.payslip.worked_days']
        mod_fuel_id = self.env['res.company'].search([('name', '=', 'Mod Fuel LLC')], limit=1).id
        joost_id = self.env['res.company'].search([('name', '=', 'Joost Vapor LLC')], limit=1).id
        joost_corp_id = self.env['res.company'].search([('name', '=', 'Joost Corp')], limit=1).id
        #Retrieve the list of employees
        employees = self.env['hr.employee'].search([])
        for employee in employees.sorted(key='id'):
            #get this employee's attendances for the pay period
            pay_period_attendances = self.env['hr.attendance'].search([
                ('employee_id', '=', employee.id),
                ('tz_check_in', '>=', pay_period['date_from'].strftime(DEFAULT_SERVER_DATETIME_FORMAT)),
                ('tz_check_in', '<=', pay_period['date_to'].strftime(DEFAULT_SERVER_DATETIME_FORMAT)),
                ('payslip_id', '=', False)])

            #go through this employee's attendances and make payslips.  If a payslip exists for the attendance, add to payslip instead
            for attendance in pay_period_attendances.sorted(key='check_in'):
                if attendance.company_id.id != joost_corp_id:
                    active_location = attendance._default_location()

                    new_payslip = self.env['hr.payslip'].search([
                        ('employee_id', '=', attendance.employee_id.id),
                        ('location_id', '=', active_location.id),
                        ('contract_id','=', attendance.contract_id.id),
                        ('company_id','=', attendance.company_id.id),
                        ('date_from','=', pay_period['date_from'].date().strftime(DEFAULT_SERVER_DATETIME_FORMAT)),
                        ('state', 'in', ['draft'])], limit=1)

                    if not new_payslip:
                        new_payslip = self.env['hr.payslip'].create_new_payslip(employee, attendance.contract_id, attendance.company_id.id, active_location, pay_period)
                        total_payslips |= new_payslip

                    #assign attendance to the payslip
                    attendance.payslip_id = new_payslip
                    self.env['hr.payslip.worked_days'].new_attendance_worked_day(new_payslip, attendance)



                #hybrid contracts
                elif attendance.company_id.id == joost_corp_id:
                    active_location = attendance._default_location()
                    #search for existing payslips based on all criteria
                    jv_payslip  = self.env['hr.payslip'].search([
                        ('employee_id', '=', attendance.employee_id.id),
                        ('location_id', '=', active_location.id),
                        ('contract_id','=', attendance.contract_id.id),
                        ('company_id','=', joost_id),
                        ('date_from','=', pay_period['date_from'].date().strftime(DEFAULT_SERVER_DATETIME_FORMAT)),
                        ('state', 'in', ['draft'])], limit=1)

                    if not jv_payslip:
                        jv_payslip  = self.env['hr.payslip'].create_new_payslip(employee, attendance.contract_id, joost_id, active_location, pay_period)
                        total_payslips |= jv_payslip

                    mf_payslip = self.env['hr.payslip'].search([
                        ('employee_id', '=', attendance.employee_id.id),
                        ('location_id', '=', active_location.id),
                        ('contract_id','=', attendance.contract_id.id),
                        ('company_id','=', mod_fuel_id),
                        ('date_from','=', pay_period['date_from'].date().strftime(DEFAULT_SERVER_DATETIME_FORMAT)),
                        ('state', 'in', ['draft'])], limit=1)

                    if not mf_payslip:
                        mf_payslip = self.env['hr.payslip'].create_new_payslip(employee, attendance.contract_id, mod_fuel_id, active_location, pay_period)
                        total_payslips |= mf_payslip

                    jv_percentage = attendance.contract_id.hybrid_joost_percent/100.0
                    #split attendance by percentages
                    jv_hours = attendance.worked_hours * jv_percentage
                    split_time = (attendance.check_in + timedelta(hours=jv_hours))
                    mf_vals = attendance.get_vals()
                    mf_vals['check_in'] = (split_time + timedelta(seconds=1)).strftime(DEFAULT_SERVER_DATETIME_FORMAT)
                    mf_vals['check_out'] = attendance.check_out
                    mf_vals['payslip_id'] = mf_payslip.id

                    attendance.write({
                        'check_out': split_time.strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                        'payslip_id': jv_payslip.id,
                    })

                    modfuel_attendance = self.env['hr.attendance'].create(mf_vals)

                    self.env['hr.payslip.worked_days'].new_attendance_worked_day(jv_payslip, attendance)
                    self.env['hr.payslip.worked_days'].new_attendance_worked_day(mf_payslip, modfuel_attendance)

            #get and apply holidays
            holidays = self.env['hr.leave'].search([
                ('employee_id', '=', employee.id),
                ('date_from', '>=', pay_period['date_from'].strftime(DEFAULT_SERVER_DATETIME_FORMAT)),
                ('date_from', '<=', pay_period['date_to'].strftime(DEFAULT_SERVER_DATETIME_FORMAT)),
                ('state', '=', 'validate'),
                ('payslip_status', '=', False)
            ])
            holidays.split_holiday()
            if holidays:
                month_attendances = self.env['hr.attendance'].search([
                    ('employee_id', '=', employee.id),
                    ('check_in', '>=', (datetime.today().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=30)).strftime(DEFAULT_SERVER_DATETIME_FORMAT)),
                    ('check_in', '<=', datetime.today().replace(hour=23, minute=59, second=59, microsecond=999999).strftime(DEFAULT_SERVER_DATETIME_FORMAT))
                ])


                hybrid_jv_percentages = month_attendances.filtered(lambda a: a.contract_id.company_id.id == joost_corp_id).mapped('contract_id').mapped('hybrid_joost_percent')
                attendance_percentage = sum(month_attendances.filtered(lambda a: a.contract_id.id == joost_id).mapped('worked_hours')) / sum(month_attendances.mapped('worked_hours'))*100
                if attendance_percentage:
                    hybrid_jv_percentages.append(attendance_percentage)
                hybrid_jv_percent = sum(hybrid_jv_percentages)/float(len(hybrid_jv_percentages))/100

                if hybrid_jv_percent:
                    #Joost Payslip to add holidays to
                    jv_payslip = total_payslips.filtered(lambda payslip: payslip.employee_id.id == employee.id and payslip.company_id.id == joost_id)[0]
                    if not jv_payslip:
                        jv_payslip  = self.env['hr.payslip'].create_new_payslip(employee, employee.contract_ids[0], joost_id, primary_employment_location, pay_period)
                        total_payslips |= jv_payslip

                    #Mod Fuel payslip to add holidays to
                    mf_payslip = total_payslips.filtered(lambda payslip: payslip.employee_id.id == employee.id and payslip.company_id.id == mod_fuel_id)[0]
                    if not mf_payslip:
                        mf_payslip = self.env['hr.payslip'].create_new_payslip(employee, employee.contract_ids[0], mod_fuel_id, primary_employment_location, pay_period)
                        total_payslips |= mf_payslip

                    #apply holidays to pay payslips
                    for holiday in holidays.sorted(key='date_from'):
                        name = _('Holiday: %s - %s') % (holiday.date_from.strftime('%Y-%m-%d'), holiday.date_to.strftime('%Y-%m-%d'))

                        #Joost worked day for current holiday
                        jv_hours = holiday.total_hours * hybrid_jv_percent
                        self.env['hr.payslip.worked_days'].new_holiday_worked_day(jv_payslip, jv_hours, name)


                        #mod fuel worked day for current holiday
                        mf_hours = holiday.total_hours - jv_hours
                        self.env['hr.payslip.worked_days'].new_holiday_worked_day(mf_payslip, mf_hours, name)


                        #Assign payslips to the holiday
                        holiday.payslip_ids |= jv_payslip
                        holiday.payslip_ids |= mf_payslip
                else:
                    active_payslip = total_payslips.filtered(lambda payslip: payslip.employee_id.id == employee.id)[0]
                    if not active_payslip:
                        active_payslip = self.env['hr.payslip'].create_new_payslip(employee, employee.contract_ids[0], employee.contract_ids[0].company_id, primary_employment_location, pay_period)
                        total_payslips |= active_payslip

                    for holiday in holidays.sorted(key='date_from'):
                        #Assign payslip to the holiday
                        holiday.payslip_ids |= active_payslip
                        #create worked day for holiday
                        name = _('Holiday: %s - %s') % (holiday.date_from.strftime('%Y-%m-%d'), holiday.date_to.strftime('%Y-%m-%d'))
                        self.env['hr.payslip.worked_days'].new_holiday_worked_day(active_payslip, holiday.total_hours, name)
                        self.env['hr.payslip.worked_days'].new_holiday_worked_day(active_payslip, holiday.total_hours, name)

        return total_payslips


class HrPayslipWorkedDays(models.Model):
    _inherit = 'hr.payslip.worked_days'


    contract_id = fields.Many2one('hr.contract', string='Contract', required=True, related='payslip_id.contract_id',
        help="The contract for which applied this input", readonly=True)
    overtime = fields.Float(string='Overtime')
    code = fields.Char(required=True, default='1', help="The code that can be used in the salary rules")

    @api.model
    def new_holiday_worked_day(self, payslip, hours, name):
        vals = {
            'payslip_id': payslip.id,
            'number_of_hours': hours,
            'name': name,
        }
        return self.env['hr.payslip.worked_days'].create(vals)

    @api.model
    def new_attendance_worked_day(self, payslip, attendance):
        vals = {
            'payslip_id': payslip.id,
            'name': attendance.check_in.date().strftime('%Y-%m-%d'),
        }
        if attendance.overtime_hours:
            vals['overtime'] =  attendance.worked_hours
        else:
            vals['number_of_hours'] =  attendance.worked_hours

        if 'overtime' in vals and not payslip.has_overtime:
            payslip.has_overtime = True

        return self.env['hr.payslip.worked_days'].create(vals)
