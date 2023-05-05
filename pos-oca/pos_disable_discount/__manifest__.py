# See LICENSE file for full copyright and licensing details.

{
    'name': 'POS Disable Discount',
    'version': '13.0.0.1.0',
    'category': 'Point Of Sale',
    'sequence': 6,
    'summary': 'POS Disable Discount',
    'description': """

POS Disable Discount

""",
    'author': 'Serpent Consulting Services Pvt. Ltd.',
    'maintainer': 'Serpent Consulting Services Pvt. Ltd.',
    'website': 'https://www.serpentcs.com',
    'license': 'AGPL-3',
    'depends': ['point_of_sale'],
    'data': [
        'view/pos_disable_discount_view.xml',
        'view/templates.xml'
    ],
    'qweb': ['static/src/xml/pos_disable_discount.xml'],
    'installable': True,
    'auto_install': False,
    'application': False,
}
