{
    'name': 'Theme Laze',
    'category': 'Theme/Ecommerce',
    'summary': "Theme Laze is a Odoo theme with advanced ecommerce feature, extremely customizable and fully responsive. It's suitable for any e-commerce sites. Start your Odoo store right away with The Laze theme",
    'version': '2.9',
    'author': 'Atharva System',
	'website' : 'http://www.atharvasystem.com',
	'license' : 'OPL-1',
    'description': """
Theme Laze is  is a Odoo theme with advanced ecommerce feature, extremely customizable and fully responsive. It's suitable for any e-commerce sites. Start your Odoo store right away with The Laze theme.
        """,
    'depends': ['website_theme_install'],
    'data': [
        'views/customize_template.xml',
        'views/templates.xml',
        'data/theme_laze_data.xml',  
    ],
    'live_test_url': 'http://theme-laze-v12.atharvasystem.com',    
	'support': 'support@atharvasystem.com',
    'images': ['static/description/laze.png','static/description/laze_screenshot.png'],
    'price': 199.00,
    'currency': 'EUR',
	'installable': True,
    'application': True,    
}
