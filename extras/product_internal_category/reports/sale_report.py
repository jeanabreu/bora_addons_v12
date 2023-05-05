# Copyright 2018 Tecnativa - David Vidal
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import fields, models


class SaleReport(models.Model):
    _inherit = "sale.report"

    product_internal_category_id = fields.Many2one(
        comodel_name='product.internal_category',
        string='Internal Category',
    )

    def _query(self, with_clause='', fields=None, groupby='', from_clause=''):
        fields = fields or {}
        fields['product_internal_category_id'] = ", t.product_internal_category_id as product_internal_category_id"
        groupby += ', t.product_internal_category_id'
        return super(SaleReport, self)._query(
            with_clause, fields, groupby, from_clause
        )