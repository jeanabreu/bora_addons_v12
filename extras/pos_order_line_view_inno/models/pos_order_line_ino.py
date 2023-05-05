# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo import tools


class pos_order_line_inno(models.Model):
    _name = 'pos.order.line.inno'
    _auto = False

    x_ref_no = fields.Char(string='Reference')
    x_create_on = fields.Datetime(string='Create On')
    x_product_name = fields.Char(string='Product')
    x_qty = fields.Integer(string='Quantity')
    x_price_unit = fields.Float(string='Unit Price')
    x_discount = fields.Float(string='Disc.%')
    x_subtotal = fields.Float(string='Subtotal w/o Tax')
    x_subtotal_tax = fields.Float(string='Subtotal')

    def init(self):
        tools.drop_view_if_exists(self._cr, 'partner_insurance_details')
        self._cr.execute("""CREATE VIEW pos_order_line_inno AS ( SELECT row_number() OVER () as id, 
        pol.name as x_ref_no, pol.create_date as x_create_on, 
        pt.name as x_product_name, pol.qty as x_qty, pol.price_unit as x_price_unit, pol.discount as x_discount,
        pol.price_subtotal as x_subtotal, pol.price_subtotal_incl as x_subtotal_tax
        from product_product pp, product_template pt, pos_order_line pol
        where pol.product_id = pp.id and pt.id = pp.product_tmpl_id)""")


