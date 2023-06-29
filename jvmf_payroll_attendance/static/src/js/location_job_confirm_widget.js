odoo.define('jvmf_payroll_attendance.location_job_confirm_widget', function (require) {
"use strict";

var AbstractAction = require('web.AbstractAction');
var core = require('web.core');
var Session = require('web.session');

var QWeb = core.qweb;

var LocJobConfirm = AbstractAction.extend({
    events: {
        "click .o_jvmf_payroll_attendance_button_cancel": function () {
            this.do_action(this.next_action, {clear_breadcrumbs: true}); },
        'click .o_jvmf_payroll_attendance_button_confirm': function() {
            var self = this;
            this.$('.o_jvmf_payroll_attendance_button_confirm').attr("disabled", "disabled");
            this._rpc({
                    model: 'hr.employee',
                    method: 'attendance_action',
                    args: [[self.employee_id], self.next_action, self.location_id, self.job_id, self.contract_id],
                })
                .then(function(result) {
                    if (result.action) {
                        self.do_action(result.action);
                    } else if (result.warning) {
                        self.do_warn(result.warning);
                        setTimeout( function() { self.$('.o_jvmf_payroll_attendance_button_confirm').removeAttr("disabled"); }, 500);
                    }
                });
        },
    },

    init: function (parent, action) {
        this.session = Session;
        this._super.apply(this, arguments);
        if(this.session.action_call_by === "my_attendances"){
            this.next_action = 'hr_attendance.hr_attendance_action_my_attendances';
        }
        else{
            this.next_action = 'hr_attendance.hr_attendance_action_kiosk_mode';
        }

        this.contract_id = action.contract_id;
        this.job_id = action.job_id;
        this.job_profile = action.job_profile;
        this.employee_id = action.employee_id;
        this.employee_name = action.employee_name;
        this.location_id = action.location_id;
        this.location_name = action.location_name;
    },

    start: function () {
        var self = this;
        self.session = Session;
        self.$el.html(QWeb.render("TestLocation", {widget: self}));
        return self._super.apply(this, arguments);
    },
});

core.action_registry.add('location_job_confirm_widget', LocJobConfirm);

return LocJobConfirm;

});
