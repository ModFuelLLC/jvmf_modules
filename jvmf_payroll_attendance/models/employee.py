# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _, SUPERUSER_ID
import logging
_logger = logging.getLogger(__name__)
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, timedelta

class Employee(models.Model):
    _inherit = 'hr.employee'

    #add to personal information
    home_phone = fields.Char('Home Phone', related='address_home_id.phone')
    mobile_phone = fields.Char('Mobile Phone', related='address_home_id.mobile')
    home_email = fields.Char('Email', related='address_home_id.email')

    #add to public or work information
    hire_date = fields.Date(string='Hire Date')

    #add for multiple locations per employee
    location_id = fields.Integer('Current Location')
    location_ids = fields.One2many('location.employee.rel', 'employee_id', string='Locations', domain=[('location_parent_id', '!=', False)])
    location_count = fields.Integer(compute='_compute_locations', store=True)
    adp_joost_employee_id = fields.Char('ADP Joost Vapor LLC. Employee ID', size=6)
    adp_modfuel_employee_id = fields.Char('ADP Mod Fuel LLC. Employee ID', size=6)

    #verifys that a primary location has been set on the employee.
    @api.constrains('location_ids')
    def check_primary_location(self):
        for employee in self:
            #if only a single location, select as default
            if len(employee.location_ids) == 1:
                employee.location_ids[0].primary_location = True
            # test for primary locations
            primary_locations = employee.location_ids.filtered(lambda p: p.primary_location == True)
            if len(primary_locations) > 1:
                raise UserError(_('Please only select a single default location.'))
            elif not len(primary_locations):
                raise UserError(_('Please select a default location.'))

    #sets the location count on the employee
    @api.multi
    def _compute_locations(self):
        for employee in self:
            employee.location_count = len(employee.location_ids)


    #indicates if an employee is a joost, mod fuel or hybrid employee
    @api.depends('company_ids')
    def _is_employee(self):
        for employee in self:
            company_names = employee.company_ids.mapped('name')
            employee.is_joost_employee = False
            employee.is_modfuel_employee = False
            if 'Joost Vapor LLC' in company_names:
                employee.is_joost_employee = True
            if 'Mod Fuel LLC' in company_names:
                employee.is_modfuel_employee = True


    company_id = fields.Many2one('res.company', string='Company', required=True,
        help='The company this user is currently working for.', context={'user_preference': True})
    company_ids = fields.Many2many('res.company', 'res_company_employees_rel', 'employee_id', 'cid',
        string='Companies')
    is_joost_employee = fields.Boolean('Is a Joost Employee', compute='_is_employee', default=False)
    is_modfuel_employee = fields.Boolean('Is a Mod Fuel Employee', compute='_is_employee', default=False)


    @api.model
    def attendance_scan(self, barcode):
        """ Receive a barcode scanned from the Kiosk Mode and change the attendances of corresponding employee.
            Returns either an action or a warning.
        """
        employee = self.search([('barcode', '=', barcode)], limit=1)
        if employee:
            if employee.attendance_state == 'checked_in':
                return employee.attendance_action('hr_attendance.hr_attendance_action_kiosk_mode')

            company_ids = employee.company_ids.ids if employee.company_ids else employee.company_id.id
            domain = [('company_ids','in',company_ids),('child_ids','=',False),('active','=',True)]
            location_objs = self.env["employment.locations"].search(domain)
            if len(location_objs) > 1:
                domain = [('id','in',location_objs.ids)]
                next_action = {
                    'name':'Locations',
                    'type':'ir.actions.act_window',
                    'res_model':'employment.locations',
                    'view_mode':'kanban',
                    'view_type':'form',
                    'views': [[self.env.ref('jvmf_payroll_attendance.location_attendance_kanban').id, 'kanban']],
                    'domain' : domain,
                    'context' : {
                      'search_default_group_by_zone': 1
                      },
                    'target':'current',
                }
                return {'action': next_action, 'employee_id': employee.id}
            if location_objs and len(location_objs) == 1:
                result = employee.get_employee_contract_action()
                result['default_loc_id'] = location_objs[0].id
                result['default_loc_name'] = location_objs[0].name
                result['employee_id'] = employee.id
                return result
            else:
                return {'warning': _('No Location Found! Please Contact HR')}
        else:
            return {'warning': _('No employee corresponding to barcode %(barcode)s') % {'barcode': barcode}}

    @api.multi
    def attendance_manual(self, next_action, entered_pin=None):
        self.ensure_one()
        if not (entered_pin is None) or self.env['res.users'].browse(SUPERUSER_ID).has_group('hr_attendance.group_hr_attendance_use_pin') and (self.user_id and self.user_id.id != self._uid or not self.user_id):
            if entered_pin != self.pin:
                return {'warning': _('Wrong PIN')}
        if self.attendance_state == 'checked_in':
            return self.attendance_action(next_action)

        company_ids = self.company_ids.ids if self.company_ids else self.company_id.id
        domain = [('company_ids','in',company_ids),('child_ids','=',False)]
        location_objs = self.env["employment.locations"].search(domain)
        if len(location_objs) > 1:
            domain = [('id','in',location_objs.ids)]
            next_action = {
                'name':'Locations',
                'type':'ir.actions.act_window',
                'res_model':'employment.locations',
                'view_mode':'kanban',
                'view_type':'form',
                'views': [[self.env.ref('jvmf_payroll_attendance.location_attendance_kanban').id, 'kanban']],
                'domain' : domain,
                'context' : {
                  'search_default_group_by_zone': 1
                  },
                'target':'current',
            }
            return {'action': next_action}
        if location_objs and len(location_objs) == 1:
            result = self.get_employee_contract_action()
            result['default_loc_id'] = location_objs[0].id
            result['default_loc_name'] = location_objs[0].name
            return result
        else:
            return {'warning': _('No Location Found! Please Contact HR')}

    @api.multi
    def attendance_action(self, next_action, location_id=None, job_id=None, contract_id=None):
        """ Changes the attendance of the employee.
            Returns an action to the check in/out message,
            next_action defines which menu the check in/out message should return to. ("My Attendances" or "Kiosk Mode")
        """
        self.ensure_one()
        action_message = self.env.ref('hr_attendance.hr_attendance_action_greeting_message').read()[0]
        action_message['previous_attendance_change_date'] = self.last_attendance_id and (self.last_attendance_id.check_out or self.last_attendance_id.check_in) or False
        action_message['employee_name'] = self.name
        action_message['next_action'] = next_action

        #allows employees with portal users to clock in and out
        modified_attendance = self.sudo().attendance_action_change(location_id, job_id, contract_id)
        action_message['attendance'] = modified_attendance.read()[0]
        return {'action': action_message}

    @api.multi
    def attendance_action_change(self, location_id=None, job_id=None, contract_id=None):
        """ Check In/Check Out action
            Check In: create a new attendance record
            Check Out: modify check_out field of appropriate attendance record
        """

        if len(self) > 1:
            raise exceptions.UserError(_('Cannot perform check in or check out on multiple employees.'))
        action_date = fields.Datetime.now()

        if self.attendance_state != 'checked_in':
            vals = {
                'employee_id': self.id,
                'check_in': action_date,
                'location_id': location_id,
                'job_id': job_id,
                'contract_id': contract_id,
            }
            return self.env['hr.attendance'].create(vals)
        else:
            attendance = self.env['hr.attendance'].search([('employee_id', '=', self.id), ('check_out', '=', False)], limit=1)
            if attendance:
                attendance.check_out = action_date
            else:
                raise exceptions.UserError(_('Cannot perform check out on %(empl_name)s, could not find corresponding check in. '
                    'Your attendances have probably been modified manually by human resources.') % {'empl_name': self.name, })
            return attendance


    @api.multi
    def get_employee_contract_action(self):
        self.ensure_one()
        default_job = self.job_id
        contract_states = ['open', 'pending']
        domain = [('employee_id','=',self.id),('state','in',contract_states)]
        hr_contracts = self.env['hr.contract'].sudo().search(domain)
        if hr_contracts and len(hr_contracts) > 1:
            next_action = {
                'name':'Contracts',
                'type':'ir.actions.act_window',
                'res_model':'hr.contract',
                'view_mode':'kanban',
                'view_type':'form',
                'views': [[self.env.ref('jvmf_payroll_attendance.hr_contract_view_kanban').id, 'kanban']],
                'domain' : domain,
                'context' : {
                  'search_default_group_by_company': 1
                  },
                'target':'current',
            }
            return {
                'action': next_action,
            }
        elif hr_contracts and len(hr_contracts) == 1:
            default_job = hr_contracts[0].job_id

        if default_job:
            return {
                'contract_id': hr_contracts[0].id if hr_contracts else 0,
                'default_job_id' : default_job.id,
                'job_name' : default_job.name,
                'employee_id' : self.id,
                'employee_name' : self.name,
            }
        else:
            return {'warning': _('No Job Profile Found! Please Contact HR')}

    @api.multi
    def _employee_events(self):
        employees = self.env['hr.employee'].search([])
        today = datetime.today()
        for employee in employees:
            hr_contact = employee.company_id.hr_contact.partner_id
            if employee.birthday and employee.birthday.strftime('%m-%d') == today.strftime('%m-%d'):
                body = "The warmest wishes to a great member of our team. May your special day be full of happiness, fun and cheer!"
                subject = ('Birthday Notification: %s') % (employee.name)
                employee.sudo().message_post(body=body, subject=subject, message_type='email', partner_ids=[hr_contact.id])
            if employee.hire_date and employee.hire_date.strftime('%m-%d') == today.strftime('%m-%d'):
                body = "I want to express my personal appreciation for your achievement of this milestone. Loyal and dedicated employees like you are the foundation to any successful company. Thank you for your contribution to our success!"
                subject = ('Anniversary Notification: %s') % (employee.name)
                employee.sudo().message_post(body=body, subject=subject, message_type='email', partner_ids=[hr_contact.id])
            if employee.hire_date and (employee.hire_date + timedelta(days=90)) == today:
                body = ('%s is ready for their 90 day review') % (employee.name)
                subject = ('90 Days Notification: %s') % (employee.name)
                employee.sudo().message_post(body=body, subject=subject, message_type='email', partner_ids=[hr_contact.id])
