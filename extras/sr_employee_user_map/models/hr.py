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


class Employee(models.Model):
    _inherit = 'hr.employee'
    
    hr_user_id = fields.Many2one('res.users', string='Mapped User')
    
    
    @api.model
    def create(self,vals):
        if not vals.get('user_id', False):
            login = vals.get('work_email', False) or vals.get('name','')
            employee_ids = self.env['res.users'].search(['|',('email','=', login),
                                                             ('login','=', login)
                                                        ])
            if employee_ids:
               raise Warning(_('User with same Login or Email already Exist'))
            else:
                user_vals = {
                            'login': login,
                            'email': login,
                            'name': vals.get('name',''),
                            'password': vals.get('name',''),
                            'image': vals.get('image',''),
                            'groups_id': [(6, 0, [
                                self.env.ref('base.group_user').id,
                                ])]
                            }
                user_id = self.env['res.users'].create(user_vals)
                vals.update({'user_id': user_id.id or False,
                             'hr_user_id': user_id.id or False})
        res = super(Employee, self).create(vals)
        return res 
    
    
    
    
            