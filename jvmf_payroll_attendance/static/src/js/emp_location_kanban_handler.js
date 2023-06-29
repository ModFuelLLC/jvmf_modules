odoo.define('jvmf_payroll_attendance.emp_location_kanban_handler', function(require) {
"use strict";

var KanbanRecord = require('web.KanbanRecord');
var Session = require('web.session');

KanbanRecord.include({
    //--------------------------------------------------------------------------
    // Private
    //--------------------------------------------------------------------------

    /**
     * @override
     * @private
     */
    _openRecord: function () {
        if (this.modelName === 'employment.locations' && this.$el.parents('.o_location_attendance_kanban').length) {
            var self = this;
            self.session = Session;
            this._rpc({
                    model: 'hr.employee',
                    method: 'get_employee_contract_action',
                    args: [[self.session.employee_id]],
                })
                .then(function(result) {
                    self.session.emp_loc_id = self.record.id.raw_value;
                    self.session.emp_loc_name = self.record.name.raw_value;
                    if (result.action) {
                        self.do_action(result.action);
                    }
                    else if (result.default_job_id) {
                        var action = {
                            type: 'ir.actions.client',
                            name: 'Locations',
                            tag: 'location_job_confirm_widget',
                            contract_id : result.contract_id,
                            job_id : result.default_job_id,
                            job_profile : result.job_name,
                            employee_id : result.employee_id,
                            employee_name : result.employee_name,
                            location_id : self.record.id.raw_value,
                            location_name : self.record.name.raw_value,
                        };
                        self.do_action(action);
                    }
                    else if (result.warning) {
                        self.do_warn(result.warning);
                    }
                });
        } else {
            this._super.apply(this, arguments);
        }
    }
});

});
