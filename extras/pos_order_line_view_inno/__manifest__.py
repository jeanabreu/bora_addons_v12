# -*- coding: utf-8 -*-
{
    'name': "POS Orderline Tree View",
    'summary': "POS Order Line Tree View",
    'description': """
        This module allows to display the POS order line into the Tree and Form View.
    """,
    'author': "Cabrel Tchomte",
    'website': "http://www.innovations-groups.com",
    'category': 'Point Of Sale',
    'version': '13.0.1.0',
    "license": "LGPL-3",
    'depends': ['point_of_sale'],
    'data': ['security/ir.model.access.csv', 'views/pos_order_line_inno.xml'],
    'images': ['static/description/pos_orderline_main_screenshot.png',
               'static/description/pos_orderline_form.png',
               'static/description/pos_orderline_groupsearch.png',
               'static/description/pos_orderline_menu.png'],
    "installable": True,
    "application": True,
    "auto_install": False,
}
