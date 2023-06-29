# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class AccountPayment(models.Model):
    _inherit = "account.payment"

    #Method to search through the check numbers of a given journal ID
        #to get the lowest unused check numbers
    #because the cancelled state has been added, cancelled check numbers remain
        #within the database and the check numbers remain "used"
    @api.model
    def get_next_check_number(self):
        #retrieves all records form the database that have check numbers
        check_numbers = sorted(self.env['account.payment'].search([
            ('journal_id', '=', self.journal_id.id),
            ('check_number', '>', 0)]).mapped('check_number'))
        #retrieve list of unused check numbers within the list of used checks
        unused_check_numbers = sorted(set(range(check_numbers[0], check_numbers[-1]+1)).difference(check_numbers)) if check_numbers else []
        #retrieve the minimum number set in the journal
        minimum_check_number = self.journal_id.minimum_check_number
        #make sure all unused check numbers are greater than or equal to the minimum
        valid_unused_check_numbers = sorted([x for x in unused_check_numbers if x >= minimum_check_number])
        #set the next check to be the lowest unused check number
        next_check = valid_unused_check_numbers[0] if valid_unused_check_numbers else self.journal_id.check_sequence_id.number_next
        #verify that the check number is valid based on the journal's minimum
        next_check = next_check if next_check >= minimum_check_number else minimum_check_number
        #verify that there are unused check numbers in the list.  If not use the next check number after the list
        if next_check in check_numbers:
            next_check = check_numbers[-1] + self.journal_id.check_sequence_id.number_increment
        return next_check

    #rewrites the print_checks method to include the get_next_check_number method above.
    @api.multi
    def print_checks(self):
        """ Check that the recordset is valid, set the payments state to sent and call print_checks() """
        # Since this method can be called via a client_action_multi, we need to make sure the received records are what we expect
        self = self.filtered(lambda r: r.payment_method_id.code == 'check_printing' and r.state != 'reconciled')

        if len(self) == 0:
            raise UserError(_("Payments to print as a checks must have 'Check' selected as payment method and "
                              "not have already been reconciled"))
        if any(payment.journal_id != self[0].journal_id for payment in self):
            raise UserError(_("In order to print multiple checks at once, they must belong to the same bank journal."))

        if not self[0].journal_id.check_manual_sequencing:
            #run the check number through the check number retrieval method
            next_check_number = self.get_next_check_number()
            view_id = self.env.ref('account_check_printing.print_pre_numbered_checks_view').id
            return {
                'name': _('Print Pre-numbered Checks'),
                'type': 'ir.actions.act_window',
                'res_model': 'print.prenumbered.checks',
                'view_type': 'form',
                'view_mode': 'form',
                'target': 'new',
                'view_id': view_id,
                'context': {
                    'payment_ids': self.ids,
                    'default_next_check_number': next_check_number,
                }
            }
        else:
            self.filtered(lambda r: r.state == 'draft').post()
            return self.do_print_checks()
