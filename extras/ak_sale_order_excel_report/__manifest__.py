# -*- coding: utf-8 -*-
# Part of Aktiv Software
# See LICENSE file for full copyright & licensing details.

{
    'name': "Sale Order Excel Report",
    'summary': """Print sale excel report SO action""",
    'description': """""",
    'author': "Aktiv Software",
    'website': "http://www.aktivsoftware.com",
    'category': 'Sales',
    'version': '13.1.1.0.0',
    'depends': [
        'sale',
    ],
    'data': [
        'report/menu_sale_xlsx.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'auto_install': False,
    'installable': True,
    'application': False,
}
