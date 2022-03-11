# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Estate Account',
    'version': '1.0',
    'category': 'Accounting/estate_account',
    'sequence': -100,
    'summary': 'estate account management',
    'description': "boh",
    'website': '',
    'license': 'LGPL-3',
    'depends': [
        'estate',
        'account'
    ],
    'data': [
        'views/estate_account_menu_views.xml'
    ],
    'demo': [],
    'qweb': [],
    'css': [],
    'application': True,
    'installable': True,
    'auto_install': False
}
