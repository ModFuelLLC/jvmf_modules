odoo.define('jvmf_payroll_attendance.my_attendances', function (require) {
"use strict";


var AbstractAction = require('web.AbstractAction');
var core = require('web.core');
var Session = require('web.session');

var QWeb = core.qweb;
var _t = core._t;

var MyAttendances = AbstractAction.extend({
    events: {
        "click .o_hr_attendance_sign_in_out_icon": function() {
            this.$('.o_hr_attendance_sign_in_out_icon').attr("disabled", "disabled");
            this.update_attendance();
        },
    },

    start: function () {
        var self = this;
        self.session = Session;
        var def = this._rpc({
                model: 'hr.employee',
                method: 'search_read',
                args: [[['user_id', '=', self.session.uid]], ['attendance_state', 'name']],
            })
            .then(function (res) {
                if (_.isEmpty(res) ) {
                    self.$('.o_hr_attendance_employee').append(_t("Error : Could not find employee linked to user"));
                    return;
                }
                self.employee = res.length && res[0];
                self.$el.html(QWeb.render("HrAttendanceMyMainMenu", {widget: self}));
            });

        return $.when(def, this._super.apply(this, arguments));
    },

    update_attendance: function () {
        var self = this;
        self.session = Session;
        self.session.action_call_by = "my_attendances";
        self.session.employee_id = self.employee.id;
        this._rpc({
                model: 'hr.employee',
                method: 'attendance_manual',
                args: [[self.employee.id], 'hr_attendance.hr_attendance_action_my_attendances'],
            })
            .then(function(result) {
                if (result.action) {
                    if (result.default_loc_id){
                        self.session.emp_loc_id = result.default_loc_id;
                        self.session.emp_loc_name = result.default_loc_name;
                    }
                    self.do_action(result.action);
                }
                else if (result.default_job_id) {
                    var action = {
                        type: 'ir.actions.client',
                        name: 'Locations',
                        tag: 'location_job_confirm_widget',
                        contract_id: result.contract_id,
                        job_id : result.default_job_id,
                        job_profile : result.job_name,
                        employee_id : result.employee_id,
                        employee_name : result.employee_name,
                        location_id : result.default_loc_id,
                        location_name : result.default_loc_name,
                    };
                    self.do_action(action);
                }
                else if (result.warning) {
                    self.do_warn(result.warning);
                }
            });
    },
});

core.action_registry.add('hr_attendance_my_attendances', MyAttendances);

return MyAttendances;

});
