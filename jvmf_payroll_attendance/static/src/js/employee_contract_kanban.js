odoo.define('jvmf_payroll_attendance.employee_contract_kanban', function(require) {
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
        if (this.modelName === 'hr.contract' && this.$el.parents('.o_hr_contract_kanban').length) {
            var self = this;
            self.session = Session;
            this._rpc({
                    model: 'hr.contract',
                    method: 'get_employee_job_position',
                    args: [[this.record.id.raw_value]],
                })
                .then(function(result) {
                    var action = {
                        type: 'ir.actions.client',
                        name: 'Locations',
                        tag: 'location_job_confirm_widget',
                        contract_id : result.contract_id,
                        job_id : result.job_id,
                        job_profile : result.job_name,
                        employee_id : result.employee_id,
                        employee_name : result.employee_name,
                        location_id : self.session.emp_loc_id,
                        location_name : self.session.emp_loc_name,
                    };
                    self.do_action(action);
                });
        } else {
            this._super.apply(this, arguments);
        }
    }
});

});
