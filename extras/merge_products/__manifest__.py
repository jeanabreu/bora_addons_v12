{
    'name': 'Merge Products',
    'version': '1.0',
    'category': 'product',
    "sequence": 1,
    'complexity': "medium",
    'description': """Merge Products""",
    'author': 'Golden Om Technology',
    'website': 'http://www.goldenomtechnology.com',
    'support':'contact@goldenomtechnology.com',
    'depends': ['product'],
    'data': [
        'security/ir.model.access.csv',
        'views/merge_products_view.xml',
          ],
    'installable': True,
    'application': False,
    'images': [],
}