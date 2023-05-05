# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions
from datetime import date
from odoo import tools, _


class Allowance(models.Model):
    _name = 'hr.allowance'
    _rec_name = 'name'
    _description = 'Allowance'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Allowance Name", required=True)
    active = fields.Boolean(string="Active", default=True)


class ContractAllowanceLine(models.Model):
    _name = 'hr.contract.allowance.line'
    _rec_name = 'allowance_id'
    _description = 'Contract Allowance Line'

    allowance_id = fields.Many2one(comodel_name="hr.allowance", string="Allowance")
    contract_id = fields.Many2one(comodel_name="hr.contract", string="Contract")
    amount = fields.Float(string="Amount")
    #Added
    es_deduccion = fields.Boolean('¿Es Deduccion?')
    es_cuota = fields.Boolean('¿Es una cuota?')

   
    
    @api.onchange('es_deduccion')
    def conv_negative(self):
        if self.es_deduccion:
            self.amount = -abs(self.amount)
        else:
            self.amount = self.amount


class Contract(models.Model):
    _name = "hr.contract"
    _inherit = 'hr.contract'

    @api.multi
    @api.constrains('state')
    def _check_state(self):
        for record in self:
            if record.state == 'open':
                contract_ids = self.env['hr.contract'].search(
                    [('employee_id', '=', record.employee_id.id), ('state', '=', 'open')])
                if len(contract_ids) > 1:
                    raise exceptions.ValidationError(_('Employee Must Have Only One Running Contract'))

    allowances_ids = fields.One2many(comodel_name="hr.contract.allowance.line", inverse_name="contract_id")
    

  

    @api.multi
    def get_all_allowances(self):
        return sum(self.allowances_ids.mapped('amount'))
    
    @api.multi
    def get_all_vivienda(self):
        regla1 = 'otrovalor'
        return sum(self.allowances_ids.\
            filtered(lambda x: x.allowance_id.name == regla1  ).mapped('amount'))
