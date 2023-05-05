# -- coding: utf-8 --
# This module and its content is copyright of Technaureus Info Solutions Pvt. Ltd.
# - © Technaureus Info Solutions Pvt. Ltd 2019. All rights reserved.

{
    'name': 'Product Image Export',
    'version': '12.0.0.3',
    'sequence': 1,
    'category': 'Inventory',
    'summary': 'Product Image Export',
    'author': 'Technaureus Info Solutions Pvt. Ltd.',
    'website': 'http://www.technaureus.com/',
    'price': 20,
    'currency': 'EUR',
    'license': 'Other proprietary',
    'description': """Product Image Export
        """,
    'depends': ['stock',
                #'report_xlsx'
                ],
    'data': [
        'report/product_report.xml',
        'wizard/product_details_view.xml',
    ],
    'images': ['images/main_screenshot.png'],
    'installable': True,
    'application': True,
    'auto_install': False,
}
