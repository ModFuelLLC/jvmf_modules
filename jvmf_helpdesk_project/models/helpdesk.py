# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _


class helpdesk_team(models.Model):
    _inherit = 'helpdesk.team'

    use_project = fields.Boolean('Project Management')
    use_communication = fields.Selection([('do_nothing', 'Do Not Copy Communication'),
                                          ('copy_all_communication',
                                           'Copy All Communication')],
                                         default='do_nothing',
                                         required=True)


class helpdesk_ticket(models.Model):
    _inherit = 'helpdesk.ticket'

    @api.multi
    @api.depends('task_ids')
    def fetch_task_timesheet(self):
        for ticket in self:
            timesheets = []
            for tasks in ticket.task_ids:
                for timesheet in tasks.timesheet_ids:
                    timesheets.append(timesheet.id)
            ticket.task_timesheet_ids = timesheets

    @api.multi
    @api.depends('task_ids')
    def count_tasks(self):
        for ticket in self:
            ticket.task_count = len(ticket.task_ids)

    @api.multi
    def create_task(self):
        self.ensure_one()
        #set task priority based on ticket priority
        task_priority = '0'
        if self.priority == '2':
            task_priority = '3'
        elif self.priority == '3':
            task_priority = '4'
        else:
            task_priority = self.priority

        vals = {
            'name': _('%s(#%s)') % (str(self.name), str(self.id)),
            'description': self.description.replace('\n', '<br />') if self.description else '',
            'project_id': self.project_id.id,
            'partner_id': self.partner_id.id,
            'user_id': self.user_id.id,
            'company_id': self.company_id.id,
            'ticket_id': self.id,
            'priority': task_priority,
        }

        new_task = self.env['project.task'].create(vals)
        #set task tags based on ticket tags
        for tag in self.tag_ids:
            new_task.tag_ids |= self.env['project.tags'].search([('name','=',tag.name)])

        task_id = new_task.id
        if self.team_id.use_communication == 'copy_all_communication':
            for message in self.message_ids.sorted(lambda r: r.id):
                message.copy({'model': 'project.task', 'res_id': task_id, 'partner_ids': False})

        docs = self.env['ir.attachment'].search([('res_model', '=', 'helpdesk.ticket'), ('res_id', '=', self.id)])
        for doc in docs:
            new_doc = doc.copy({'res_model': 'project.task', 'res_id': task_id})

    @api.multi
    def show_ticket_tasks(self):
        self.ensure_one()
        ticket_id = self.id
        action = self.env.ref('project.action_view_task')
        if ticket_id:
            return{
                'name': action.name,
                'type': action.type,
                'view_type': action.view_type,
                'view_mode': action.view_mode,
                'target': action.target,
                'res_model': action.res_model,
                'domain': [('ticket_id', '=', ticket_id)],
                }

    @api.multi
    def total_hours(self):
        for ticket in self:
            ticket.hours_spent = sum(ticket.task_timesheet_ids.mapped('unit_amount'))

    project_id = fields.Many2one('project.project', 'Project')
    project_checked = fields.Boolean('Project Management',
                                     related='team_id.use_project')
    task_ids = fields.One2many('project.task', 'ticket_id', 'Task')
    task_count = fields.Integer('Task', compute='count_tasks', store=True)
    task_timesheet_ids = fields.One2many('account.analytic.line',
                                         string='Task Timesheet',
                                         compute='fetch_task_timesheet')
    hours_spent = fields.Float('Hours Spent', compute='total_hours')
    helpdesk_timesheet_ids = fields.One2many('account.analytic.line',
                                             'ticket_id',
                                             'Helpdesk Timesheet')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
