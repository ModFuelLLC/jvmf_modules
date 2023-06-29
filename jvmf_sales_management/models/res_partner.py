# coding: utf-8

from odoo import api, fields, models

class Partner(models.Model):
    _inherit = 'res.partner'



    edit_salesperson = fields.Boolean(compute='_compute_edit_salesperson', default='_compute_edit_salesperson')
    user_id = fields.Many2one('res.users', string='Salesperson',
        help='The internal user that is in charge of communicating with this contact if any.')

    #Limits who can edit the salesperson field
    @api.model
    def _compute_edit_salesperson(self):
        for rec in self:
            rec.edit_salesperson = True
            if rec.parent_id:
                rec.edit_salesperson = False
            else:
                rec.edit_salesperson = self.env.user.has_group('jvmf_sales_management.group_edit_salesperson')

    #auto sets the sales person to the current user
    @api.onchange('customer')
    @api.constrains('customer')
    def compute_salesperson(self):
        if self.customer and not self.user_id:
            self.user_id = self.env.user

    @api.onchange('parent_id')
    def _inherit_salesperson(self):
        for rec in self:
            if rec.parent_id:
                rec.user_id = rec.parent_id.user_id
            rec._compute_edit_salesperson()


    @api.model
    def create(self,vals):
        #Force salesperson to match parent's salesperson
        for partner in self:
            if 'parent_id' in vals:
                parent_id = self.env['res.partner'].search([('id','=',vals['parent_id'])])
                if parent_id.user_id.id != vals['user_id']:
                    vals['user_id'] = parent_id.user_id.id

        res = super(Partner, self).create(vals)
        return res

    @api.multi
    def write(self, vals):
        """Function is designed to assign the Salesperson and delivery method to a contact.
        This function will allow for a Company Salesperson and delivery method to be set to an individual
        from that Company if the individual doesn't already have a salesperson or delivery method
        associated with them. """
        #salesperson ineritance
        for partner in self:
            #if this record has a parent record
            if partner.parent_id and partner.user_id != partner.parent_id.user_id:
                vals['user_id'] = partner.parent_id.user_id.id
            #if this record is a parent record
            if partner.child_ids:
                for child in partner.child_ids:
                    partner_user_id = partner.user_id.id
                    if 'user_id' in vals and child.user_id.id != vals['user_id']:
                            partner_user_id = vals['user_id']
                    if child.user_id.id != partner_user_id:
                        child.write({'user_id': partner_user_id})


        res = super(Partner, self).write(vals)
        return res
