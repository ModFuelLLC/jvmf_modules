# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class PrintPreNumberedChecks(models.TransientModel):
    _inherit = 'print.prenumbered.checks'

    #check to see if the check number has already been used and changes it
        #to the next unused number
    @api.multi
    def action_test_check_number(self):
        #obtain payment information
        next_check_number = self.next_check_number
        payments = self.env['account.payment'].browse(self.env.context['payment_ids'])
        payments.filtered(lambda r: r.state == 'draft').post()
        #get the checks from the databse based on the journal id and puts them into a sorted list
        check_numbers = sorted(self.env['account.payment'].search([
            ('journal_id', '=', payments.journal_id.id),
            ('check_number', '>', 0)]).mapped('check_number'))
        #Checks to see if the check number from the form view has been used,
        #if so a dialogue box comes up indicating that there is a duplicate check number.
        if next_check_number in check_numbers:
            view_id = self.env.ref('jvmf_check_number_sequencing.duplicate_check_numbers').id
            return {
                'name': 'Duplicate Check Numbers',
                'type': 'ir.actions.act_window',
                'res_model': 'print.prenumbered.checks',
                'view_type': 'form',
                'view_mode': 'form',
                'target': 'new',
                'view_id': view_id,
            }
        else:
            return self.print_checks(payments, next_check_number)

    #overwrites the print checks method to include the get_check_number method above
    @api.multi
    def print_checks(self, payments, check_number):
        payments.filtered(lambda r: r.state != 'sent').write({'state': 'sent'})
        for payment in payments:
            payment.check_number = check_number
            payment.journal_id.check_sequence_id.number_next = payment.get_next_check_number()
        return payments.do_print_checks()
