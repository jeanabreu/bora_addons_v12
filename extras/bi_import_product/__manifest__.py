# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Import Product and update Product from Excel Odoo',
    'version': '12.0.0.1',
    'category' : 'Sales',
    "price": 8,
    "currency": 'EUR',
    'summary': 'Apps for import product import product template import product data import product variants import update product update product template update product data update product template import product from excel import product from xls import products data',
    'description': """
	
    import products from Excel file in odoo,
    import products in odoo apps,
    from excel import products in odoo,
    import products from XLS file in odoo,
    multiple products import from XLS file in odoo,
    

    """,
    'author': 'BrowseInfo',
    'website': 'https://www.browseinfo.in',
    'depends': ['base','sale','sale_management','stock','purchase'],
    'data': [
         "views/product_view.xml",    
             ],
	'qweb': [
		],
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
    'live_test_url':'https://youtu.be/cGsYnbks148',
    "images":["static/description/Banner.png"],
}
