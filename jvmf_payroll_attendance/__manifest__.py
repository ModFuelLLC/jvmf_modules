# -*- coding: utf-8 -*-
{
    'name': "Payroll and Attendance",

    'summary': """
        An extension to the attendences module to include multiple locations and jobs.
        """,

    'description': """
        \n1. Creates a system for Employment Locations and allows employees to select a location and position when clocking in.
        \n2. Locations displayed at clock in are limited by assigned companies.
        \n3. Also extended employee records to list assigned locations and companies.
        \n4. All employees assigned to locations will show a phone list in the location as well as inherited up to the zones.
        \n5. Zones also show a list of locations and employee phone list within that zone.
        \n6. System will automatically clock out employees after 13.5 hours.
        \n7. Hid contract information behind manager permissions to further lock down kiosk access.
        \n8. Assigned Zone and Location managers have relevant locations (for zone managers all locations in zone) assigned to their employee records.
        \n9. Added location, zone, and job information to attendances.
        \n10. Granted access to Manual Attendance group to open and view the kiosk as well as view their own attendances.
        \n11. Added dynamic filters for the current pay period and previous pay period based on config setting for beginning of a pay period.
    """,

    'author': "Mod Fuel LLC",
    'website': "",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Human Resources',
    'version': '12.0.1.0',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'hr',
        'hr_recruitment',
        'hr_attendance',
        'hr_contract',
        'hr_payroll',
        'website',
        ],

    # always loaded
    'data': [
        'data/ir_cron.xml',
        'security/ir.model.access.csv',
        'views/attendance.xml',
        'views/res_config_settings.xml',
        'views/contract.xml',
        'views/employment_locations.xml',
        'views/employee.xml',
        'views/hr_leave.xml',
        'views/hr_payroll_views.xml',
        'views/job.xml',
        'views/res_company.xml',
        'views/templates.xml',
        'wizard/hr_contract_wizard_view.xml',
    ],
    'qweb': [
        "static/xml/new_attendance.xml",
    ],
    'application': True,
}
