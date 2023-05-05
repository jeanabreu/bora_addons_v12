# -- coding: utf-8 --
# This module and its content is copyright of Technaureus Info Solutions Pvt. Ltd.
# - © Technaureus Info Solutions Pvt. Ltd 2019. All rights reserved.

from odoo import fields, models, api, _


class ProductDetailsWizard(models.TransientModel):
    _name = 'product.details.wizard'

    based_on = fields.Selection([
        ('products', 'Productos Seleccionados'),
        ('category', 'Categoria de Productos')
    ], required=True, default='products', string='Basado en')

    category_id = fields.Many2one('product.category', string='Categoria de Productos')
    product_details_report = fields.Binary(string='Productos')

    def export_details(self):
        context = self._context
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'product.details.wizard'
        datas['form'] = self.read()[0]
        return self.env.ref('tis_product_image_export.product_report_xls').report_action(self, data=datas)
