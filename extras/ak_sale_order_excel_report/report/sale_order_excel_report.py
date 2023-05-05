# -*- coding: utf-8 -*-
# Part of Aktiv Software
# See LICENSE file for full copyright & licensing details.

from odoo import models

class PartnerXlsx(models.AbstractModel):
    _name = 'report.ak_sale_order_excel_report.sale_xlsx'
    _description = 'Sale Oder Excle Report'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, partners):
        for obj in partners:
            customer_data = ''
            company_format = workbook.add_format(
                {'bg_color': 'black', 'align': 'center', 'font_size': 25,
                    'font_color': 'white'})
            order_format = workbook.add_format(
                {'bg_color': 'black', 'align': 'center', 'font_size': 14,
                    'font_color': 'white', 'border': 1})
            table_header_left = workbook.add_format(
                {'bg_color': 'black', 'align': 'left', 'font_size': 12,
                    'font_color': 'white'})
            table_row_left = workbook.add_format(
                {'align': 'left', 'font_size': 12, 'border': 1})
            table_header_right = workbook.add_format(
                {'bg_color': 'black', 'align': 'right', 'font_size': 12,
                    'font_color': 'white', 'border': 1})
            table_row_right = workbook.add_format(
                {'align': 'right', 'font_size': 12, 'border': 1})
            customer_header_format = workbook.add_format({
                'align': 'center', 'font_size': 13, 'bold': True, 'border': 1})
            customer_format = workbook.add_format({
                'align': 'center', 'font_size': 13, 'border': 1})
            table_left = workbook.add_format(
                {'align': 'left', 'bold': True, 'border': 1})
            table_right = workbook.add_format(
                {'align': 'right', 'bold': True, 'border': 1})
            if obj.partner_id.name:
                customer_data += obj.partner_id.name + '\n'
            if obj.partner_id.street:
                customer_data += obj.partner_id.street + '\n'
            if obj.partner_id.street2:
                customer_data += obj.partner_id.street2 + '\n'
            if obj.partner_id.city:
                customer_data += obj.partner_id.city + ' '
            if obj.partner_id.state_id:
                customer_data += str(obj.partner_id.state_id.name + ' ')
            if obj.partner_id.zip:
                customer_data += obj.partner_id.zip + ' '
            if obj.partner_id.country_id:
                customer_data += '\n' + str(obj.partner_id.country_id.name)
            worksheet = workbook.add_worksheet(obj.name)
            worksheet.merge_range('A2:F3', obj.company_id.name, company_format)
            worksheet.merge_range('A4:F4', '')
            if obj.state not in ['draft', 'sent']:
                worksheet.merge_range(
                    'A5:F5', 'Order :- ' + obj.name, order_format)
                worksheet.merge_range(
                    'C7:D7', 'Order Date', customer_header_format)
                worksheet.merge_range(
                    'E7:F7', str(obj.date_order.date()), customer_format)
            elif obj.state in ['draft', 'sent']:
                worksheet.merge_range(
                    'A5:F5', 'Quotation :- ' + obj.name, order_format)
                worksheet.merge_range(
                    'C7:D7', 'Quotation Date', customer_header_format)
                worksheet.merge_range(
                    'E7:F7', str(obj.date_order.date()), customer_format)
            worksheet.merge_range('A6:F6', '')
            worksheet.merge_range(
                'A7:B7', 'Customer', customer_header_format)
            worksheet.merge_range(
                'A8:B12', customer_data, customer_format)
            worksheet.merge_range(
                'C8:D8', 'Salesperson', customer_header_format)
            worksheet.merge_range(
                'E8:F8', obj.user_id.name, customer_format)
            if obj.client_order_ref:
                worksheet.merge_range(
                    'C9:D9', 'Your Reference', customer_header_format)
                worksheet.merge_range(
                    'E9:F9', obj.client_order_ref, customer_format)
                if obj.payment_term_id:
                    worksheet.merge_range(
                        'C10:D10', 'Payment Terms', customer_header_format)
                    worksheet.merge_range(
                        'E10:F10', obj.payment_term_id.name, customer_format)
            elif obj.payment_term_id:
                worksheet.merge_range(
                    'C9:D9', 'Payment Terms', customer_header_format)
                worksheet.merge_range(
                    'E9:F9', obj.payment_term_id.name, customer_format)
            worksheet.merge_range('A13:I13', '')

            row = 14
            worksheet.set_column('A:A', 40)
            worksheet.set_column('B:B', 15)
            worksheet.set_column('C:C', 15)
            worksheet.set_column('D:D', 15)
            worksheet.set_column('E:E', 15)
            worksheet.set_column('F:F', 15)

            group = self.env.user.has_group(
                'product.group_discount_per_so_line')
            display_discount = any([l.discount for l in obj.order_line])
            display_tax = any([l.tax_id for l in obj.order_line])
            worksheet.write(row, 0, 'Producto', table_header_left)
            worksheet.write(row, 1, 'Cantidad', table_header_right)
            worksheet.write(row, 2, 'Precio Unit', table_header_right)
            worksheet.write(row, 6, 'Tipo', table_header_right)
            worksheet.write(row, 7, 'Cod de Barra', table_header_right)
            worksheet.write(row, 8, 'Tamano', table_header_right)
            worksheet.write(row, 9, 'PPK', table_header_right)
            worksheet.write(row, 10, 'Codigo de Producto', table_header_right)
            if display_discount and group:
                worksheet.write(row, 3, 'Disc.%', table_header_right)
                if display_tax:
                    worksheet.write(row, 4, 'Taxes', table_header_right)
                    worksheet.write(row, 5, 'Amount', table_header_right)
                else:
                    worksheet.write(row, 4, 'Amount', table_header_right)
            elif display_tax:
                worksheet.write(row, 3, 'Taxes', table_header_right)
                worksheet.write(row, 4, 'Amount', table_header_right)
            else:
                worksheet.write(row, 3, 'Amount', table_header_right)
            row += 1

            for line in obj.order_line:
                worksheet.write(row, 0, line.name, table_row_left)
                worksheet.write(row, 1, line.product_uom_qty, table_row_right)
                worksheet.write(row, 2, line.price_unit, table_row_right)
                worksheet.write(row, 6, line.x_studio_tipo_fisico, table_row_right)
                worksheet.write(row, 7, line.x_studio_cod_barra, table_row_right)
                worksheet.write(row, 8, line.x_studio_tamao, table_row_right)
                worksheet.write(row, 9, line.x_studio_ppk, table_row_right)
                worksheet.write(row, 10, line.x_studio_codigo_del_producto, table_row_right)
                
                if display_discount and group:
                    worksheet.write(row, 3, line.discount, table_row_right)
                    if display_tax and line.tax_id:
                        worksheet.write(
                            row, 4, line.tax_id.name, table_row_right)
                        worksheet.write(
                            row, 5, line.price_subtotal, table_row_right)
                        row += 1
                    elif not line.tax_id and display_tax:
                        worksheet.write(row, 4, '0', table_row_right)
                        worksheet.write(
                            row, 5, line.price_subtotal, table_row_right)
                        row += 1
                    else:
                        worksheet.write(
                            row, 4, line.price_subtotal, table_row_right)
                        row += 1
                elif display_tax:
                    if display_tax and line.tax_id:
                        worksheet.write(
                            row, 3, line.tax_id.name, table_row_right)
                        worksheet.write(
                            row, 4, line.price_subtotal, table_row_right)
                        row += 1
                    elif not line.tax_id:
                        worksheet.write(row, 3, '0', table_row_right)
                        worksheet.write(
                            row, 4, line.price_subtotal, table_row_right)
                        row += 1
                    else:
                        worksheet.write(
                            row, 3, line.price_subtotal, table_row_right)
                        row += 1
                else:
                    worksheet.write(
                        row, 3, line.price_subtotal, table_row_right)
                    row += 1
            if display_discount and group and display_tax:
                worksheet.merge_range(row, 0, row, 5, '')
                worksheet.write(row + 1, 4, 'Untaxed Amount', table_left)
                worksheet.write(row + 1, 5, obj.amount_untaxed, table_right)
                worksheet.write(row + 2, 4, 'Taxes', table_left)
                worksheet.write(row + 2, 5, obj.amount_tax, table_right)
                worksheet.write(row + 3, 4, 'Total', table_left)
                worksheet.write(row + 3, 5, obj.amount_total, table_right)
            elif not group and not display_tax and not display_discount:
                worksheet.merge_range(row, 0, row, 3, '')
                worksheet.write(row + 1, 2, 'Subtotal', table_left)
                worksheet.write(row + 1, 3, obj.amount_untaxed, table_right)
                worksheet.write(row + 2, 2, 'Total', table_left)
                worksheet.write(row + 2, 3, obj.amount_total, table_right)
            elif not group and not display_tax:
                worksheet.merge_range(row, 0, row, 3, '')
                worksheet.write(row + 1, 2, 'Subtotal', table_left)
                worksheet.write(row + 1, 3, obj.amount_untaxed, table_right)
                worksheet.write(row + 2, 2, 'Total', table_left)
                worksheet.write(row + 2, 3, obj.amount_total, table_right)
            elif not display_tax and not display_discount:
                worksheet.merge_range(row, 0, row, 3, '')
                worksheet.write(row + 1, 2, 'Subtotal', table_left)
                worksheet.write(row + 1, 3, obj.amount_untaxed, table_right)
                worksheet.write(row + 2, 2, 'Total', table_left)
                worksheet.write(row + 2, 3, obj.amount_total, table_right)
            elif group and display_discount:
                worksheet.merge_range(row, 0, row, 4, '')
                worksheet.write(row + 1, 3, 'Subtotal', table_left)
                worksheet.write(row + 1, 4, obj.amount_untaxed, table_right)
                worksheet.write(row + 2, 3, 'Total', table_left)
                worksheet.write(row + 2, 4, obj.amount_total, table_right)
            elif display_tax:
                worksheet.merge_range(row, 0, row, 4, '')
                worksheet.write(row + 1, 3, 'Subtotal', table_left)
                worksheet.write(row + 1, 4, obj.amount_untaxed, table_right)
                worksheet.write(row + 2, 3, 'Taxes', table_left)
                worksheet.write(row + 2, 4, obj.amount_tax, table_right)
                worksheet.write(row + 3, 3, 'Total', table_left)
                worksheet.write(row + 3, 4, obj.amount_total, table_right)
