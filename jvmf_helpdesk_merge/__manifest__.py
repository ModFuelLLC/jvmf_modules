# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.

{
    'name': 'Helpdesk Ticket Merge',
    'version': '12.0.0',
    'category': 'Helpdesk',
    "author": "Bizzappdev, Mod Fuel LLC.",
    "website": "http://bizzappdev.com",
    'sequence': 10,
    'depends': [
        'helpdesk', 'mail', 'jvmf_helpdesk_project',
    ],
    'description': """
Helpdesk Ticket Merge
=====================

    """,
    'data': [
        'data/merge_ticket_email_view.xml',
        'wizard/merge_ticket_view.xml',
        'view/helpdesk_views.xml',
        'view/helpdesk_team_view.xml',
    ],
    'qweb': [
    ],
    'price': 99,
    'currency': 'EUR',
    'application': True,
    'auto_install': False,
    'images': ['images/Selection_01.png'],
    'license': 'Other proprietary',
}
