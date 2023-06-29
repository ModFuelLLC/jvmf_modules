# -*- coding: utf-8 -*-
{
    'name': "Check Number Sequencing",

    'summary': """
        Resequencing of check numbers to be more intuitive""",

    'description': """
        The following functionality has been added to Account Payments and Check Printing.


        \n - Check number sequencing has been retooled to find gaps in the check numbers in the database and fill them.
        \n - When attempting to print a check or record a check the system has a 3 level check.
        \n\t - Level One - A manually entered number in the journal settings setting a minimum check number.
        \n\t\t - This allows the user to set a starting piont or a way to force a gap in the sequence, such as for unusable checks.
        \n\t - Level Two - A dynamically set check number stored in the sequence to work as a starting point.
        \n\t\t - This number should be the lowest unused check number that is higher than the minimum check number.
        \n\t - Level Three - The system grabs all of the check numbers for a particular journal and if neither of the two above options are triggered it grabs the lowest currently used check number to begin it's cycle.
        \n - When a user manually enters a check number for record keeping, such as using a pre-printed check, the check number will not only be compared to the existing check numbers but will allow for the system to continue to use all unused check numbers between the last printed check and the manually entered check.
    """,

    'author': "Mod Fuel LLC",
    'website': "",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Accounting',
    'version': '12.0.1.0',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'account',
        'account_check_printing',
        ],

    # always loaded
    'data': [
        'views/print_prenumbered_checks_views.xml',
        'views/account_payment_views.xml',
        'views/account_journal_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [

    ],
}
