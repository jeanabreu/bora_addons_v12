# -*- coding: utf-8 -*-
from odoo import models, fields, api


class HrContract(models.Model):
    _inherit = 'hr.contract'

    recurringinput_ids = fields.One2many('hr.contract.recurringinput', 'contract_id', string='Recurring Input')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
