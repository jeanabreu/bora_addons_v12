# Copyright 2014 - Vauxoo http://www.vauxoo.com/
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# Copyright 2017 Serpent Consulting Services Pvt. Ltd.
#   (<http://www.serpentcs.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Hr Payroll Cancel",
    "version": "12.0.1.0.1",
    "author": "Vauxoo, Eficent, "
              "Serpent Consulting Services Pvt. Ltd.,"
              "Odoo Community Association (OCA)",
    "category": "HR",
    "website": "https://github.com/OCA/hr",
    "license": "AGPL-3",
    "depends": [
        "account_cancel",
    ],
    "data": [
        "views/hr_payslip_view.xml",
    ],
    "installable": True,
}
