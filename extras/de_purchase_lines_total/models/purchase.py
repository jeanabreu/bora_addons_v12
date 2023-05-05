from odoo import models, fields, api

class PickingTotalQty(models.Model):
    _inherit = 'purchase.order'

    tot_purchase_qty = fields.Float(compute='_calculate_purchase_qty', string='Total Cant. Comprada', help="Total cantidad comprada en este documento")

    def _calculate_purchase_qty(self):
        for rs in self:
            sumqty = 0
            for line in rs.order_line:
                sumqty += line.product_qty
        rs.tot_purchase_qty = sumqty


