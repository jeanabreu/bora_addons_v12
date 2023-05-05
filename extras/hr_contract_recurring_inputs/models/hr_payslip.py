# -*- coding: utf-8 -*-
from odoo import models, fields, api


class HrPayslipInput(models.Model):
    _inherit = 'hr.payslip.input'

    from_recurringinput = fields.Boolean(string='From Recurring-Input', default=False)
#Para v12#    
    input_type_id = fields.Many2one('hr.payslip.input.type', string='Type', required=True, domain="['|', ('id', 'in', _allowed_input_type_ids), ('struct_ids', '=', False)]")
    _allowed_input_type_ids = fields.Many2many('hr.payslip.input.type', related='payslip_id.struct_id.input_line_type_ids')

class HrPayrollStructure(models.Model):
    _inherit = 'hr.payroll.structure'

    input_line_type_ids = fields.Many2many('hr.payslip.input.type', string='Other Input Line')

class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

   
    @api.onchange('employee_id', 'struct_id', 'contract_id', 'date_from', 'date_to')
    def onchange_employee(self):
        res = super(HrPayslip, self).onchange_employee()
        if self.contract_id and self.date_from and self.date_to:
            other_input_list = []
            self.input_line_ids = False
            for each in self.contract_id.recurringinput_ids.filtered(lambda x:x.active_recurringinput == True):
                input_line_ids = self.input_line_ids.filtered(lambda x:x.from_recurringinput == True and x.input_type_id == each.input_type_id)
                if each.end_date and each.start_date <= self.date_from and each.end_date >= self.date_to:
                    other_input_list.append((0, 0, {
                        'input_type_id': each.input_type_id.id,
                        'amount': each.amount,
                        'from_recurringinput': True}
                        ))
                if not each.end_date and each.start_date <= self.date_from:
                    other_input_list.append((0, 0, {
                        'input_type_id': each.input_type_id.id,
                        'amount': each.amount,
                        'from_recurringinput': True}
                        ))
            self.input_line_ids = other_input_list
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
