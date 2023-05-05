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


from odoo import api, models, fields, _
from odoo.exceptions import Warning


class EmpUSerWizard(models.TransientModel):
    _name = 'emp.user.wizard'
    _description="EmpUSerWizard"
    
    @api.model
    def default_get(self, fields):
        res = super(EmpUSerWizard, self).default_get(fields)
        emp_obj = self.env['hr.employee']
        dom = [('user_id', '=', False)]
        emp_ids = emp_obj.search(dom)
        if emp_ids:
            res.update({'emp_ids': [(6, 0, emp_ids.ids)]})
        return res
    
    
    emp_ids = fields.Many2many('hr.employee', 'emp_wizard_rel', 'wiz_id', 'emp_id',
                               string='Employes')
    
    
    
    @api.multi
    def add_user(self):
        for record in self:
            mapped_emps = []
            res = True
            for emp in record.emp_ids:
                if emp.user_id:
                    continue
                
                dom = [('email','=', emp.work_email or ''), ('login','=', emp.name or '')]
                user_ids = self.env['res.users'].search(dom)
                if user_ids:
                   user_id = user_ids and user_ids.ids[0] or False
                else:
                    login = emp.work_email or emp.name
                    user_vals = {
                                'login': emp.name,
                                'email': emp.work_email,
                                'name': emp.name,
                                'password': emp.name,
                                'image': emp.image,
                                'groups_id': [(6, 0, [
                                    self.env.ref('base.group_user').id,
                                    ])]
                                }
                    user_obj = self.env['res.users'].create(user_vals)
                    user_id = user_obj.id
                emp.write({'user_id': user_id or False,
                           'hr_user_id': user_id or False})
                mapped_emps.append(emp.id)
            res = self.view_active_employee(mapped_emps)
            return res
        
    @api.multi 
    def view_active_employee(self, mapped_emps):
        action = self.env.ref('hr.open_view_employee_list_my')
        result = {
            'name': action.name,
            'type': action.type,
            'view_type': action.view_type,
            'view_mode': action.view_mode,
            'target': 'current',
            'res_model': action.res_model,
        }
        result['domain'] = str([('id','in',mapped_emps)])
        return result    
