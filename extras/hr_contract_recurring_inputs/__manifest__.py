# -*- coding: utf-8 -*-
{
    "name" : "HR Contract Recurring-Inputs",
    'summary' : "HR Contract Recurring-Inputs",
    "version" : "13.0",
    "description": """HR Contract Recurring-Inputs""",
    'author' : 'Dhruvil Goswami',
    'category' : 'HR',
    'website' : 'dhruvil.gosai@yahoo.com',
    'price': 30,
    'currency': 'EUR',
    "depends": ['base', 
                'hr', 
                'hr_payroll',
                'hr_contract'],
    "data": [
        'views/recurring_input_views.xml',
        'views/hr_contract_views.xml',
        'views/hr_payroll_view.xml',
        'security/ir.model.access.csv',
    ],
    "auto_install": False,
    "installable": True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: