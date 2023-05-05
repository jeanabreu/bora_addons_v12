# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions, _


class HrContractRecurringInput(models.Model):
    _name = 'hr.contract.recurringinput'
    _description = 'HR Contract Recurring Input'
    name = fields.Char(string="Name")
    contract_id = fields.Many2one('hr.contract', string='Contract')
    input_type_id = fields.Many2one('hr.payslip.input.type', string='Input Type')
    amount = fields.Monetary(string='Amount')
    currency_id = fields.Many2one(string="Currency", related='contract_id.company_id.currency_id', readonly=True)
    start_date = fields.Date(string='Start Date')
    end_date = fields.Date(string='End Date')
    active_recurringinput = fields.Boolean(string='Active', default=True)

    @api.model
    def create(self, vals):
        contract_id = self.env['hr.contract'].browse(vals.get('contract_id'))
        name = contract_id.name + ': ' + vals.get('start_date') + ' a ' + (vals.get('end_date') if vals.get('end_date') else '~')
        vals.update({'name': name})
        return super(HrContractRecurringInput, self).create(vals)

    @api.onchange('contract_id', 'start_date', 'end_date')
    def onchange_dates(self):
        name = ((self.contract_id and self.contract_id.name) or '-') + ': '
        name += ((self.start_date and str(self.start_date)) or '~') + ' to ' 
        name += (self.end_date and str(self.end_date)) or '~'
        self.update({'name': name})

    @api.constrains('start_date', 'end_date')
    def check_date(self):
        if self.end_date and self.start_date > self.end_date:
            raise exceptions.ValidationError('Please enter valid Dates!')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
