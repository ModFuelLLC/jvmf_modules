# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import logging
_logger = logging.getLogger(__name__)
from odoo.addons.base.models.res_partner import _tz_get
from odoo.exceptions import UserError, ValidationError

class LocationEmployeeRel(models.Model):
    _name = 'location.employee.rel'


    #make related table so that there is a virtual many2many relationship
    #keeping both the locations table and the employee table clean
    employee_id = fields.Many2one('hr.employee', string='Employee')
    employee_home_phone = fields.Char(related='employee_id.home_phone', string='Employee Home Phone', readonly=True)
    employee_mobile_phone = fields.Char(related='employee_id.mobile_phone', string='Employee Mobile Phone', readonly=True)
    name = fields.Char(related='location_id.name', string='Location Name', readonly=True)
    location_id = fields.Many2one('employment.locations', string='Location')
    location_address_id = fields.Many2one('res.partner', related='location_id.address_id', string='Location Address', readonly=True)
    location_phone_number = fields.Char(related='location_id.phone_number', string='Work Phone', readonly=True)
    location_parent_id = fields.Many2one('employment.locations', related='location_id.parent_id', string='Zone', readonly=True)
    primary_location = fields.Boolean(string='Default Location', default=False)

    #Inherits employee and locations to zones
    @api.constrains('employee_id')
    def parent_employees(self):
        if self.location_id.parent_id:
            parent_employees = []
            for parent_employee in self.location_id.parent_id.employee_ids:
                parent_employees.append(parent_employee.employee_id)
            #make a list of the of the child's (self) employees
            child_employees = []
            for child_employee in self.location_id.employee_ids:
                child_employees.append(child_employee.employee_id)
            #cycle through each employee in child's list
            for employee in child_employees:
                #test if employee already in parent's employee list
                if employee not in parent_employees:
                    #if not in list set values for employee
                    emp_vals = {
                        'employee_id': employee.id,
                        'location_id': self.location_id.parent_id.id,
                    }
                    #add to parents list
                    self.env['location.employee.rel'].create(emp_vals)


class EmploymentLocations(models.Model):
    _name = 'employment.locations'
    _parent_name = "parent_id"
    _inherit = ['mail.thread', 'mail.activity.mixin', 'resource.mixin']


    #allow for children to be found and populated
    @api.multi
    def _compute_children(self):
        for location in self:
            location.child_count = len(location.child_ids)

    @api.multi
    def _compute_employees(self):
        for location in self:
            location.employee_count = len(location.employee_ids)

    @api.multi
    def _payroll_location(self):
        for location in self:
            location.payroll_location = False
            if location.parent_id:
                    location.payroll_location = True

    def _edit_payroll_location(self):
        for rec in self:
            rec.can_edit_payroll_location = self.env.user.has_group('hr.group_hr_manager')

    #build the Employment Locations table
    name = fields.Char('Name')
    address_id = fields.Many2one('res.partner', 'Address')
    phone_number = fields.Char('Phone Number',related='address_id.phone', readonly=True)
    parent_id = fields.Many2one('employment.locations', string='Zone')
    child_ids = fields.One2many('employment.locations','parent_id', readonly=True)
    child_count = fields.Integer(compute='_compute_children', string='Number of Stores in Zone')
    employee_ids = fields.One2many('location.employee.rel', 'location_id', domain=[('employee_id.active','=', True)], string='Employee', readonly=True)
    employee_count = fields.Integer(compute='_compute_employees', string='Number of Employees')
    adp_joost_location_id = fields.Char('ADP Joost Vapor LLC. Location ID', size=6)
    adp_modfuel_location_id = fields.Char('ADP Mod Fuel LLC. Location ID', size=6)
    location_timezone = fields.Selection(_tz_get, string='Timezone', default='US/Eastern', requried=True)
    #    \nWhen green this location  \nWhen gray this defaults to the employees default location."
    payroll_location = fields.Boolean(default=_payroll_location, string='Payroll Location',
        help="Indicates whether a location can be used for payroll, Green - Yes, Gray - No")
    can_edit_payroll_location = fields.Boolean(compute=_edit_payroll_location)
    active = fields.Boolean('Active', related='resource_id.active', default=True, store=True, readonly=False)


    #set zone Manager
    @api.constrains('parent_id')
    def _get_zone_manager(self):
        for loc in self:
            if loc.parent_id:
                loc.zone_manager_id = loc.parent_id.zone_manager_id

    #Manager information
    location_manager_id = fields.Many2one('hr.employee', string="Location Manager")
    zone_manager_id = fields.Many2one('hr.employee', string="Zone Manager", compute=_get_zone_manager, store=True)

    #Set the ability to select companies for each location
    @api.model
    def _get_company(self):
        return self.env.user.company_id

    @api.constrains('parent_id')
    def _get_companies(self):
        for loc in self:
            if loc.parent_id:
                loc.company_ids = loc.parent_id.company_ids


    company_id = fields.Many2one('res.company', string='Company', required=True, default=_get_company,
        help='The company this user is currently working for.', context={'user_preference': True})
    company_ids = fields.Many2many('res.company', 'res_company_locations_rel', 'location_id', 'cid',
        string='Companies', compute=_get_companies, store=True)

    @api.constrains('company_ids')
    def _is_location(self):
        for loc in self:
            company_names = []
            for company in loc.company_ids:
                company_names.append(company.name)
            if 'Joost Vapor LLC' in company_names:
                loc.is_joost_loc = True
            if 'Mod Fuel LLC' in company_names:
                loc.is_modfuel_loc = True

    is_joost_loc = fields.Boolean('Is a Joost Location', compute='_is_location', default=False)
    is_modfuel_loc = fields.Boolean('Is a Mod Fuel Location', compute='_is_location', default=False)


    #inherit Zone manager to locations as zone manager, and set each location to the zone managers location_ids
    @api.model
    def assign_zone_manager(self, related_location):
        for loc in self:
            if loc.parent_id and loc.zone_manager_id != loc.parent_id.zone_manager_id:
                loc.zone_manager_id = loc.parent_id.zone_manager_id.id
                if loc not in loc.zone_manager_id.location_ids.mapped('location_id'):
                    zone_manager_vals = {
                        'employee_id': loc.zone_manager_id.id,
                        'location_id': loc.id,
                    }
                    related_location.create(zone_manager_vals)
            if not loc.parent_id:
                if loc.child_ids:
                    for child in loc.child_ids:
                        if child.zone_manager_id != loc.zone_manager_id:
                            child.zone_manager_id = loc.zone_manager_id.id
                            if loc not in loc.zone_manager_id.location_ids('location_id'):
                                manager_vals = {
                                    'employee_id': child.zone_manager_id.id,
                                    'location_id': child.id,
                                }
                                related_location.create(manager_vals)
        for emp in self.mapped('zone_manager_id'):
            emp_locs = emp.location_ids.filtered(lambda p: p.primary_location == True)
            if not emp_locs:
                emp.location_ids[0].primary_location = True
            elif len(emp_locs) > 1:
                for emp_loc in emp_locs:
                    emp_loc.primary_location = False
                emp_locs[0].primary_location = True

    #set location to location manager's location_ids
    @api.model
    def assign_location_manager(self, related_location):
        for loc in self:
            if loc.location_manager_id and loc not in loc.location_manager_id.location_ids.mapped('location_id'):
                emp_vals = {
                    'employee_id': loc.location_manager_id.id,
                    'location_id': loc.id,
                    'primary_location': True,
                }
                for emp_loc in loc.location_manager_id.location_ids.filtered(lambda p: p.primary_location == True):
                    emp_loc.primary_location = False
                related_location.create(emp_vals)

    #after editing record, inherit company_ids
    @api.multi
    def write(self, vals):
        res = super(EmploymentLocations, self).write(vals)
        related_location = self.env['location.employee.rel']
        # Companies for child, default to parent's
        if self.parent_id and self.company_ids != self.parent_id.company_ids:
            for location in self:
                location.company_ids = self.parent_id.company_ids

        #if Child, pass employees up to parent
        if self.parent_id:
            #make a list of the parent's employees
            parent_employees = []
            for parent_employee in self.parent_id.employee_ids:
                parent_employees.append(parent_employee.employee_id)
            #make a list of the of the child's (self) employees
            child_employees = []
            for child_employee in self.employee_ids:
                child_employees.append(child_employee.employee_id)
            #cycle through each employee in child's list
            for employee in child_employees:
                #test if employee already in parent's employee list
                if employee not in parent_employees:
                    #if not in list set values for employee
                    emp_vals ={
                        'employee_id': employee.id,
                        'location_id': self.parent_id.id,
                    }
                    #add to parents list
                    related_location.create(emp_vals)

        # update child's companies when parent partner's companies are updated
        if not self.parent_id:
            #test of parent has children
            if self.child_ids:
                #cycle through each child to test/add employees
                for child in self.child_ids:
                    #inherit child companies
                    child.company_ids = self.company_ids
                    #make list of parent's (self) employees
                    parent_employees = []
                    for parent_employee in self.employee_ids:
                        parent_employees.append(parent_employee.employee_id)
                    #make list of children's employees
                    child_employees = []
                    for child_employee in child.employee_ids:
                        child_employees.append(child_employee.employee_id)

                    #cycle through all employees in this child's employees
                    for employee in child_employees:
                        #test if child's employee is already apart of the parent' employees
                        if employee not in parent_employees:
                            #set values for employee if not already apart of the parent
                            emp_vals ={
                                'employee_id': employee.id,
                                'location_id': self.id,
                            }
                            #add employee to the parent's employees
                            related_location.create(emp_vals)

        self.assign_zone_manager(related_location)
        self.assign_location_manager(related_location)

        return res
