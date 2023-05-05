# -- coding: utf-8 --
# This module and its content is copyright of Technaureus Info Solutions Pvt. Ltd.
# - © Technaureus Info Solutions Pvt. Ltd 2019. All rights reserved.

from odoo import fields, models, api, _
import io
import base64


class ProductXlsx(models.AbstractModel):
    _name = 'report.tis_product_image_export.product_report_xls.xslx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, wizard_obj):
        worksheet = workbook.add_worksheet('Report')
        bold = workbook.add_format({'bold': True, 'align': 'center'})
        text = workbook.add_format({'font_size': 12, 'align': 'center'})
        if wizard_obj.category_id:
            rec = self.env['product.product'].search([('categ_id', '=', wizard_obj.category_id.id)])
        else:
            rec = self.env[data['context'].get('active_model')].search([('id', 'in', data['ids'])])
        worksheet.set_column(0, 2, 15)
        worksheet.set_column(3, 4, 25)
        worksheet.set_column(5, 7, 15)
        worksheet.set_column(8, 8, 25)
        worksheet.write('A1', 'ITEM', bold)
        worksheet.write('B1', 'FOTO', bold)
        worksheet.write('C1', 'Referencia', bold)
        worksheet.write('D1', 'Codigo de Barra', bold)
        worksheet.write('E1', 'Descripcion', bold)
        worksheet.write('F1', 'Unidad de Medida', bold)
        worksheet.write('G1', 'PPK', bold)
        worksheet.write('H1', 'Size', bold)
        worksheet.write('I1', 'Genero', bold)
        worksheet.write('J1', 'Color', bold)
        worksheet.write('K1', 'Marca', bold)
        worksheet.write('L1', 'Tipo', bold)
        worksheet.write('M1', 'Categoria', bold)
        worksheet.write('N1', 'Sub-Categoria', bold)
        worksheet.write('O1', 'Existencia en Cormont', bold)
        worksheet.write('P1', 'Precio al Detalle', bold)
        worksheet.write('Q1', 'Precio al Detalle con ITBIS', bold)
        worksheet.write('R1', 'Precio al por mayor', bold)
        worksheet.write('S1', 'Precio al por mayor con ITBIS', bold)
        #worksheet.write('R1', 'Existencia por Almacen(es)', bold)
        
        row = 1
        col = 0
        row_num = 1
        for product in rec:
            worksheet.set_row(row_num, 52)
            worksheet.write(row, col, row_num, text)
            row_num = row_num + 1
            if product.image_small:
                buf_image = io.BytesIO(base64.b64decode(product.image_small))
                worksheet.insert_image(row, col + 1, "product.png", {'image_data': buf_image})
            worksheet.write(row, col + 2, product.default_code, text)
            worksheet.write(row, col + 3, product.barcode, text)
            worksheet.write(row, col + 4, product.name, text)
            worksheet.write(row, col + 5, product.uom_id.name, text)
            worksheet.write(row, col + 6, product.x_studio_ppk_1.x_name, text)
            worksheet.write(row, col + 7, product.x_studio_field_Zipzw.x_name, text)
            worksheet.write(row, col + 8, product.x_studio_genero.x_name, text)
            worksheet.write(row, col + 9, product.x_studio_color_1, text)
            worksheet.write(row, col + 10, product.product_brand_id.name, text)
            worksheet.write(row, col + 11, product.x_studio_tipo_de_producto_fisico, text)
            worksheet.write(row, col + 12, product.categ_id.name, text)
            worksheet.write(row, col + 13, product.description_sale, text)
            worksheet.write(row, col + 14, product.x_studio_cantidad_en_cormort_22, text)
            worksheet.write(row, col + 15, product.lst_price, text)
            worksheet.write(row, col + 16, product.x_precio_con_itbis, text)
            worksheet.write(row, col + 17, product.x_studio_ultimo_precio_al_mayor, text)
            worksheet.write(row, col + 18, product.x_precio_al_por_mayor_con_itbis, text)
            #worksheet.write(row, col + 17, product.warehouse_quantity, text)
            
            row = row + 1
