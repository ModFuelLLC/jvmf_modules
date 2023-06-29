# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.
from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError


class MergeTicket(models.TransientModel):
    _name = 'merge.ticket'
    _description = 'Merge Ticket'

    @api.model
    def _get_body(self):
        Template = self.env['mail.template']
        template = self.env['ir.model.data'].xmlid_to_object('helpdesk_merge.merge_ticket_email_template')
        ticket_id = self.env['helpdesk.ticket'].browse(
            self._context.get('active_id'))
        if template:
            body_html = Template.with_context(
                {'master_ticket_name': ticket_id.display_name}).render_template(
                    template.body_html, 'helpdesk.ticket',
                    self._context.get('active_id'))
            return body_html

    @api.model
    def _get_subject(self):
        Template = self.env['mail.template']
        ticket_id = self.env['helpdesk.ticket'].browse(
            self._context.get('active_id'))
        template = self.env['ir.model.data'].xmlid_to_object(
            'helpdesk_merge.merge_ticket_email_template')
        if template:
            subject = Template.with_context({
                'master_ticket_name': ticket_id.display_name
            }).render_template(template.subject,
                               'helpdesk.ticket',
                               self._context.get('active_id'))
            return subject

    @api.model
    def get_ticket(self):
        return self._context.get('active_id')

    @api.model
    def get_default_stage(self):
        active_id = self.get_ticket()
        ticket_id = self.env['helpdesk.ticket'].browse(active_id)
        return ticket_id.stage_id

    stage_id = fields.Many2one('helpdesk.stage', 'Stage', default=get_default_stage)
    ticket_ids = fields.Many2many('helpdesk.ticket',
                                  'helpdesk_ticket_rel',
                                  'helpdesk_id',
                                  'ticket_id',
                                  string='Tickets')
    ticket_id = fields.Many2one('helpdesk.ticket',
                                'Ticket',
                                default=get_ticket)
    ticket_team_id = fields.Many2one('helpdesk.team', related='ticket_id.team_id', readonly=True, string='Team')
    body = fields.Html('Body', default=_get_body)
    subject = fields.Char('Subject', default=_get_subject)
    email = fields.Selection(related='ticket_id.team_id.email')

    @api.multi
    def get_data(self):
        self.ensure_one()
        context = dict(self._context or {})
        active_id = context.get('active_id', self.ticket_id.id)
        parent_ticket_id = self.env['helpdesk.ticket'].browse(active_id)
        Mail = self.env['mail.mail']
        comment_id = self.env.ref('mail.mt_comment').id
        note_id = self.env.ref('mail.mt_note').id
        if parent_ticket_id.team_id.communication == 'copy_all_communication':
            for message in self.ticket_ids.mapped('message_ids').filtered(lambda a: a.subtype_id.id in [comment_id, note_id]).sorted(reverse=True):
                old_id = message.res_id
                message.write({'model': 'helpdesk.ticket',
                               'res_id': active_id})
                message.copy({'partner_ids': False, 'res_id': old_id})
        for merged_ticket in self.ticket_ids:
            if merged_ticket.description:
                args = {
                    'msg': parent_ticket_id.description or '',
                    'msg1': '======================================',
                    'msg2': 'Ticket: %s(#%s)' % (merged_ticket.name, str(merged_ticket.id)),
                    'msg3': "Customer: %s" % (merged_ticket.partner_id.name or ''),
                    'msg4': "Location: %s" % (merged_ticket.location.name or ''),
                    'msg5': "Department: %s" % (merged_ticket.department.name or ''),
                    'msg6': "Description:\n\n%s" % (merged_ticket.description or '')}
                description_format = "%(msg)s\n%(msg1)s\n%(msg2)s\n%(msg3)s\n%(msg4)s\n%(msg5)s\n%(msg6)s"
                description = description_format % args
                parent_ticket_id.write({'description': description})
            if parent_ticket_id.team_id.email == 'send_mail':
                recipient_ids = [(4, pid.partner_id.id) for pid in merged_ticket.message_follower_ids]
                body = self.body.replace("TICKETNAME", merged_ticket.display_name)
                subject = self.subject.replace("TICKETNAME",
                                               merged_ticket.display_name)
                mail = Mail.create({'recipient_ids': recipient_ids,
                                    'body_html': body,
                                    'subject': subject,
                                    'res_id': merged_ticket.id,
                                    'model': 'helpdesk.ticket',
                                    'auto_delete': True})
                mail.send()
            merged_ticket.with_context(merge_ticket=True).write({
                'stage_id': self.stage_id.id,
                'is_merge': True,
                'parent_id': parent_ticket_id.id,
                'user_id': parent_ticket_id.user_id.id,
            })

            if merged_ticket.project_id and not parent_ticket_id.project_id:
                parent_ticket_id.project_id = merged_ticket.project_id

            #move tasks to the new ticket
            for task in merged_ticket.task_ids:
                task.ticket_id = parent_ticket_id

            #copy documents to new ticket
            docs = self.env['ir.attachment'].search([('res_model', '=', 'helpdesk.ticket'), ('res_id', '=', merged_ticket.id)])
            for doc in docs:
                doc.copy({'res_model': 'helpdesk.ticket', 'res_id': parent_ticket_id.id})

            for child in merged_ticket.child_ids:
                #If merging a ticket that has already had children, inherit the merges into the new ticket.
                child.parent_id = merged_ticket.parent_id
                #move child ticket tasks to the new ticket
                for task in child.task_ids:
                    task.ticket_id = parent_ticket_id

            #set Parent Ticket priority to Highest priority of all involved tickets.
            priorities = parent_ticket_id.child_ids.mapped('priority')
            priorities.append(parent_ticket_id.priority)
            parent_ticket_id.priority = sorted(priorities, reverse=True)[0]

            for tag in merged_ticket.tag_ids:
                parent_ticket_id.tag_ids |= tag

            if merged_ticket.active:
                merged_ticket.toggle_active()
            parent_ticket_id.write({'merged_ids': [(4, merged_ticket.id)]})
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
