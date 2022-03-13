# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'ESTATE',
    'version': '1.0',
    'category': 'Sales/ESTATE',
    'sequence': -100,
    'summary': 'estate management',
    'description': "",
    'website': 'https://www.odoo.com/page/estate',
    'license': 'LGPL-3',
    'depends': [
        'base_setup',
    ],
    'data': [
        'data/ir.model.access.csv',
        'data/security.xml',
        'views/estate_menu_views.xml',
        'views/estate_property_view.xml',
        'views/estate_property_type_view.xml',
        'views/res_users_views.xml',
        'views/css_loader.xml',
    ],
    'demo': [],
    'qweb': [],
    'css': ['static/src/css/crm.css'],
    'application': True,
    'installable': True,
    'auto_install': False
}
