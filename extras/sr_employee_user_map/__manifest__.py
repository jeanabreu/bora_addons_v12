# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2016 SEEROO IT SOLUTIONS PVT.LTD(<https://www.seeroo.com/>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
     'name': 'Employee User Map',
    'version': '1.0',
    'author': 'Seeroo',
    'website': 'www.seeroo.com',
    'category': 'Human Resources',
    'depends': ['hr',],
    'demo': [],
    'description': """
When Employee create, automatically User created and maped to Related user field 
    """,
    'data': [
            'wizard/emp_user_wizard_view.xml',
            'menu.xml',
            ],
    'images': [
        'static/description/banner.jpg',
        ],
   'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'AGPL-3',
    'author': 'Seeroo IT Solutions',
    'website': 'https://www.seeroo.com',
}

