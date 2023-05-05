# -*- coding: utf-8 -*-

# Copyright (C) 2019-2020 Garazd Creation (<https://garazd.biz/>)
# Author: Yurii Razumovskyi (<support@garazd.biz>)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

{
    'name': 'Custom Product Labels 50x25 mm',
    'version': '12.0.1.0.2',
    'category': 'Extra Tools',
    'author': 'Garazd Creation',
    'website': "https://garazd.biz",
    'license': 'LGPL-3',
    'summary': """Print custom product labels 50x25 mm""",
    'images': ['static/description/banner.png'],
    'description': """
        The module adds the product label template with size 50 x 25 mm (2 x 1 ") and a barcode for label printers, makers.
    """,
    'depends': [
        'garazd_product_label',
    ],
    'data': [
        'report/product_label_reports.xml',
        'report/product_label_templates.xml',
    ],
    'price': 25.0,
    'currency': 'EUR',
    'support': 'support@garazd.biz',
    'application': False,
    'installable': True,
    'auto_install': False,
}
