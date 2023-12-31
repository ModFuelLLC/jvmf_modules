# Copyright 2013 Agile Business Group sagl (<http://www.agilebg.com>)
# Copyright 2016 ACSONE SA/NA (<http://acsone.eu>)

{
    'name': "Optional quick create",
    'version': '12.0.1.0.0',
    'category': 'Tools',
    'summary': "Avoid 'quick create' on m2o fields, on a 'by model' basis",
    'author': "Agile Business Group, Odoo Community Association (OCA)",
    'website': 'http://github.com/OCA/server-ux',
    'license': 'AGPL-3',
    'depends': ['base'],
    'data': [
        'views/model_view.xml',
    ],
    'installable': True,
}
