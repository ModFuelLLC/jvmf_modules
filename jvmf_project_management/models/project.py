# coding: utf-8
from datetime import timedelta

from odoo import api, fields, models, tools, SUPERUSER_ID, _
from odoo.exceptions import UserError, AccessError, ValidationError
from odoo.tools.safe_eval import safe_eval


class ProjectTaskType(models.Model):
    _inherit = 'project.task.type'

    def _is_project_manager(self):
        for rec in self:
            rec.is_project_manager = self.env.user.has_group('project.group_project_manager')

    wip_limit = fields.Integer(string='Work in Progress Limit(WIP)')
    is_project_manager = fields.Boolean(compute="_is_project_manager")

    @api.multi
    def name_get(self):
        result = []
        for type in self:
            name = type.name
            if type.wip_limit > 0:
                name += '(' + str(type.wip_limit) + ')'
            result.append((type.id, name))
        return result


## This class extends Project.task to increase the number of stars on each Project Task.
class ProjectTask(models.Model):
    _inherit = 'project.task'

    #Increases the priority system to allow for more granular priorities
    priority = fields.Selection([
        ('0', 'Low'),
        ('1','Moderately Low'),
        ('2','Moderate'),
        ('3','Moderatly High'),
        ('4','High'),
        ('5','Critical')
    ])

    #Subtask progress bar
    def _compute_subtask_progress(self):
        for task in self:
            if task.subtask_count:
                done_subtasks = self.env['project.task'].search([('parent_id', '=', task.id), ('stage_id.fold', '=', True)])
                done_subtasks_count = len(done_subtasks)
                task.subtask_progress = (done_subtasks_count*100)/task.subtask_count

    subtask_progress = fields.Float(string='Subtask Progress', compute='_compute_subtask_progress')

    #subtask control - Allows for subtasks to be turned on and off based on the project instead of the user. Set on project
    use_subtasks = fields.Boolean(related="project_id.use_subtasks", string='Use Subtasks')

    def _compute_prs(self):
        for task in self:
            task.pr_count = len(task.pr_ids)

    #Additional data fields that will allow project users to have more searchable data available
    module_name = fields.Char(string='Module Name')
    pull_request = fields.Char(string='Pull Request')
    git_branch = fields.Char(string='Git Branch')
    website_link = fields.Char(string='Web Address')
    collaborator_ids = fields.Many2many('res.users','project_task_users_rel', 'task_id', 'user_id', domain="[('share','=',False), ('id', '!=', user_id)]", string='Collaborators')

    def _compute_collaborators(self):
        for task in self:
            task.collaborator_count = len(task.collaborator_ids)

    collaborator_count = fields.Integer(string='Number of collaborators', compute='_compute_collaborators')
    pr_ids = fields.Many2many('purchase.request', 'pr_project_rel', 'task_id', 'user_id', string='Purchase Requests')
    pr_count = fields.Integer(string='Number of Purchase Requests', compute='_compute_prs')
    related_task = fields.Many2one('project.task', string='Related Task', domain="[('id', '!=', id)]")
    related_tasks = fields.One2many('project.task', 'related_task', string='Related Tasks', readonly=True)

    def _related_task_count(self):
        for task in self:
            task.related_task_count = len(task.related_tasks)

    related_task_count = fields.Integer(compute=_related_task_count)


    #form control fields for additional fields
    view_module_name_form = fields.Boolean(related='project_id.view_module_name_form', readonly=True)
    view_pull_request_form = fields.Boolean(related='project_id.view_pull_request_form', readonly=True)
    view_git_branch_form = fields.Boolean(related='project_id.view_git_branch_form', readonly=True)
    view_collaborators_form = fields.Boolean(related='project_id.view_collaborators_form', readonly=True)
    view_pr_form = fields.Boolean(related='project_id.view_pr_form', readonly=True)
    view_related_task_form = fields.Boolean(related='project_id.view_related_task_form', readonly=True)
    view_website_link_form = fields.Boolean(related='project_id.view_website_link_form', readonly=True)

    #kanban control fields for additional Fields
    view_module_name_kanban = fields.Boolean(related='project_id.view_module_name_kanban', readonly=True)
    view_pull_request_kanban = fields.Boolean(related='project_id.view_pull_request_kanban', readonly=True)
    view_git_branch_kanban = fields.Boolean(related='project_id.view_git_branch_kanban', readonly=True)
    view_collaborators_kanban = fields.Boolean(related='project_id.view_collaborators_kanban', readonly=True)
    view_pr_kanban = fields.Boolean(related='project_id.view_pr_kanban', readonly=True)
    view_related_task_kanban = fields.Boolean(related='project_id.view_related_task_kanban', readonly=True)
    view_website_link_kanban = fields.Boolean(related='project_id.view_website_link_kanban', readonly=True)


    @api.multi
    def _compute_attachment_number(self):
        read_group_res = self.env['ir.attachment'].read_group(
            [('res_model', '=', 'project.task'), ('res_id', 'in', self.ids)],
            ['res_id'], ['res_id'])
        attach_data = { res['res_id']: res['res_id_count'] for res in read_group_res }
        for record in self:
            record.attachment_number = attach_data.get(record.id, 0)

    attachment_number = fields.Integer(compute='_compute_attachment_number', string="Number of Attachments")


    @api.multi
    def action_get_attachment_tree_view(self):
        attachment_action = self.env.ref('base.action_attachment')
        action = attachment_action.read()[0]
        action['domain'] = str(['&', ('res_model', '=', self._name), ('res_id', 'in', self.ids)])
        return action

    @api.constrains('collaborator_ids', 'user_id')
    def assign_collaborators(self):
        partner = self.env.user.partner_id
        for task in self:
            collaborators = task.collaborator_ids.mapped('partner_id')
            collaborators |= task.user_id.partner_id
            collaborators |= task.manager_id.partner_id
            partner_ids = []
            for follower in task.message_follower_ids:
                if follower.partner_id not in collaborators:
                    message = "<ul><li>%s has been removed from %s</li></ul>" % (follower.partner_id.name, task.name)
                    task.sudo().message_post(body=message, message_type='notification', author_id=partner.id)
                    follower.sudo().unlink()
            for collaborator in collaborators:
                if collaborator not in task.message_partner_ids:
                    partner_ids.append(collaborator.id)
                    message = "<ul><li>%s is a collaborator for %s</li></ul>" % (collaborator.name, task.name)
                    task.sudo().message_post(body=message, message_type='notification', author_id=partner.id)
            task.sudo().message_subscribe(partner_ids=partner_ids)

    @api.onchange('stage_id')
    @api.constrains('stage_id')
    def check_wip_limit(self):
        for task in self:
            wip = len(self.env['project.task'].search([('project_id', '=', task.project_id.id), ('stage_id', '=', task.stage_id.id)]))
            wip_limit = task.stage_id.wip_limit
            stage_name = task.stage_id.name
            if wip_limit > 0 and wip > wip_limit:
                if wip > 2:
                    raise UserError(_('You cannot move %s into stage %s. \n\n%s has a Work in Progress Limit (WIP Limit) of %s.  \n\nPlease complete the tasks in %s before adding another task.') %
                        (task.name, stage_name, stage_name, str(wip_limit), stage_name))
                else:
                    raise UserError(_('You cannot move %s into stage %s. \n\n%s has a Work in Progress Limit (WIP Limit) of %s.  \n\nPlease complete the task in %s before adding another task.') %
                        (task.name, stage_name, stage_name, str(wip_limit), stage_name))

    @api.multi
    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
        rec = super(ProjectTask, self).copy()
        for predecessor in self.predecessor_ids:
            vals = predecessor.copy_data(default)[0]
            vals['task_id'] = rec.id
            pred = self.env['project.task.predecessor'].create(vals)
        return rec





class Project(models.Model):
    _inherit = "project.project"

    #turn subtasks on/off per project
    use_subtasks = fields.Boolean(string='Use Subtasks')

    #form control fields for additional fields.  Controls for all tasks within project
    view_module_name_form = fields.Boolean(string='Module Name')
    view_pull_request_form = fields.Boolean(string='Pull Request')
    view_git_branch_form = fields.Boolean(string='Git Branch')
    view_collaborators_form = fields.Boolean(string='Form Collaborators')
    view_pr_form = fields.Boolean(string='Purchase Requests')
    view_related_task_form = fields.Boolean(string='Related Task')
    view_website_link_form = fields.Boolean(string='Web Address')

    #kanban control fields for additional fields.  Controls for all tasks within project
    view_module_name_kanban = fields.Boolean(string='Module Name')
    view_pull_request_kanban = fields.Boolean(string='Pull Request')
    view_git_branch_kanban = fields.Boolean(string='Git Branch')
    view_collaborators_kanban = fields.Boolean(string='Kanban Collaborators')
    view_pr_kanban = fields.Boolean(string='Purchase Requests')
    view_related_task_kanban = fields.Boolean(string='Related Task')
    view_website_link_kanban = fields.Boolean(string='Web Address')


    #Control to check to turn off kanban when form is turned off
    @api.multi
    def check_form(self,form,kanban):
        if not form and kanban:
            kanban = False
        return kanban

    #control to check to turn on form if Kanban is turned on
    @api.multi
    def check_kanban(self,form,kanban):
        if kanban and not form:
            form = True
        return form

    #Individual field controls to check to verify kanban view is only on if the form view is on.
    @api.onchange('view_website_link_kanban')
    def check_web_link_kanban(self):
        new_state = self.check_kanban(self.view_website_link_form, self.view_website_link_kanban)
        if self.view_website_link_form != new_state:
            self.view_website_link_form = new_state

    @api.onchange('view_website_link_form')
    def check_web_link_form(self):
        new_state = self.check_form(self.view_website_link_form, self.view_website_link_kanban)
        if self.view_website_link_kanban != new_state:
            self.view_website_link_kanban = new_state

    @api.onchange('view_module_name_kanban')
    def check_module_name_kanban(self):
        new_state = self.check_kanban(self.view_module_name_form, self.view_module_name_kanban)
        if self.view_module_name_form != new_state:
            self.view_module_name_form = new_state

    @api.onchange('view_module_name_form')
    def check_module_name_form(self):
        new_state = self.check_form(self.view_module_name_form, self.view_module_name_kanban)
        if self.view_module_name_kanban != new_state:
            self.view_module_name_kanban = new_state

    @api.onchange('view_pull_request_kanban')
    def check_pull_request_name_kanban(self):
        new_state = self.check_kanban(self.view_pull_request_form,self.view_pull_request_kanban)
        if self.view_pull_request_form != new_state:
            self.view_pull_request_form = new_state

    @api.onchange('view_pull_request_form')
    def check_pull_request_name_form(self):
        new_state = self.check_form(self.view_pull_request_form,self.view_pull_request_kanban)
        if self.view_pull_request_kanban != new_state:
            self.view_pull_request_kanban = new_state

    @api.onchange('view_git_branch_kanban')
    def check_git_branch_name_kanban(self):
        new_state = self.check_kanban(self.view_git_branch_form,self.view_git_branch_kanban)
        if self.view_git_branch_form != new_state:
            self.view_git_branch_form = new_state


    @api.onchange('view_git_branch_form')
    def check_git_branch_name_form(self):
        new_state = self.check_form(self.view_git_branch_form,self.view_git_branch_kanban)
        if self.view_git_branch_kanban != new_state:
            self.view_git_branch_kanban = new_state

    @api.onchange('view_collaborators_kanban')
    def check_collaborators_name_kanban(self):
        new_state = self.check_kanban(self.view_collaborators_form,self.view_collaborators_kanban)
        if self.view_collaborators_form != new_state:
            self.view_collaborators_form = new_state

    @api.onchange('view_collaborators_form')
    def check_collaborators_name_form(self):
        new_state = self.check_form(self.view_collaborators_form,self.view_collaborators_kanban)
        if self.view_collaborators_kanban != new_state:
            self.view_collaborators_kanban = new_state

    @api.onchange('view_pr_kanban')
    def check_pr_kanban(self):
        new_state = self.check_kanban(self.view_pr_form,self.view_pr_kanban)
        if self.view_pr_form != new_state:
            self.view_pr_form = new_state

    @api.onchange('view_pr_form')
    def check_pr_form(self):
        new_state = self.check_form(self.view_pr_form,self.view_pr_kanban)
        if self.view_pr_kanban != new_state:
            self.view_pr_kanban = new_state

    @api.onchange('view_related_task_kanban')
    def check_related_task_kanban(self):
        new_state = self.check_kanban(self.view_related_task_form,self.view_related_task_kanban)
        if self.view_related_task_form != new_state:
            self.view_related_task_form = new_state

    @api.onchange('view_related_task_form')
    def check_related_task_form(self):
        new_state = self.check_form(self.view_related_task_form,self.view_related_task_kanban)
        if self.view_related_task_kanban != new_state:
            self.view_related_task_kanban = new_state

class Users(models.Model):
    _inherit = 'res.users'

    #Many2many field to reference Collaborators
    project_task_ids = fields.Many2many('project.task','project_task_users_rel', 'user_id', 'task_id', string='Collaborators')


class PurchaseRequest(models.Model):
    _inherit = 'purchase.request'

    #Many2many field to reference Purchase Requests
    project_task_ids = fields.Many2many('project.task','pr_project_rel', 'pr_id', 'task_id', string='Related Tasks')
