from odoo import models, fields, api

class PickingTotalQty(models.Model):
    _inherit = 'stock.picking'

    sum_done_qty = fields.Float(compute='calculate_sum_qty', string='Cantidad Lista')
    sum_dmd_qty = fields.Float(compute='calculate_dmd_qty', string='Cantidad Demandada')

    def calculate_sum_qty(self):
        for rs in self:
            sumqty = 0
            for line in rs.move_lines:
                sumqty += line.quantity_done
        rs.sum_done_qty = sumqty

    def calculate_dmd_qty(self):
        for rs in self:
            dmdqty = 0
            for line in rs.move_lines:
                dmdqty += line.product_uom_qty
        rs.sum_dmd_qty = dmdqty
