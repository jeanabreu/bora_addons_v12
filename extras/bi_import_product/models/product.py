# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

import tempfile
import binascii
import xlrd
from odoo.exceptions import Warning
from odoo import models, fields, exceptions, api, _
import time
from datetime import date, datetime
import io
import logging
_logger = logging.getLogger(__name__)

try:
    import xlwt
except ImportError:
    _logger.debug('Cannot `import xlwt`.')
try:
    import cStringIO
except ImportError:
    _logger.debug('Cannot `import cStringIO`.')
try:
    import base64
except ImportError:
    _logger.debug('Cannot `import base64`.')

class gen_product(models.TransientModel):
    _name = "gen.product"

    file = fields.Binary('File',required=True)
    product_option = fields.Selection([('create','Create Product'),('update','Update Product')],string='Option', required=True,default="create")
    product_search = fields.Selection([('by_code','Search By Code'),('by_name','Search By Name'),('by_barcode','Search By Barcode')],string='Search Product')

    @api.multi
    def create_product(self, values):
        product_obj = self.env['product.product']
        product_categ_obj = self.env['product.category']
        product_uom_obj = self.env['uom.uom']
        product_season_obj = self.env['product.season']

        if values.get('categ_id')=='':
            raise Warning(_('CATEGORY field can not be empty'))
        else:
            categ_id = product_categ_obj.search([('name','=',values.get('categ_id'))],limit=1)
            if not categ_id:
                raise Warning(_('Category %s not found.' %values.get('categ_id') ))

#season
        if values.get('season_id')=='':
            raise Warning(_('Temporada no puede estar vacio'))
        else:
            season_id = product_season_obj.search([('name','=',values.get('season_id'))],limit=1)
            if not season_id:
                raise Warning(_('Temporada1 %s no encontrada.' %values.get('season_id') ))  

        
        if values.get('type') == 'Consumable':
            categ_type ='consu'
        elif values.get('type') == 'Service':
            categ_type ='service'
        elif values.get('type') == 'Storable Product':
            categ_type ='product'
        else:
            categ_type = 'product'
        
        if values.get('uom_id')=='':
            uom_id = 1
        else:
            uom_search_id  = product_uom_obj.search([('name','=',values.get('uom_id'))])
            if not uom_search_id:
                raise Warning(_('UOM %s not found.' %values.get('uom_id') ))
            uom_id = uom_search_id.id
        
        if values.get('uom_po_id')=='':
            uom_po_id = 1
        else:
            uom_po_search_id  = product_uom_obj.search([('name','=',values.get('uom_po_id'))])
            if not uom_po_search_id:
                raise Warning(_('Purchase UOM %s not found' %values.get('uom_po_id') ))
            uom_po_id = uom_po_search_id.id

        if values.get('name') == '':
            barcode = False
            raise Warning(_('Please give name of the Product'))
        else:
            barcode = values.get('name').split(".")

        if values.get('barcode') == '':
            barcode = False
            raise Warning(_('Please give barcode of the Product'))
        else:
            barcode = values.get('barcode').split(".")
        vals = {
                  'name':values.get('name'),
                  'default_code':values.get('default_code'),
                  'categ_id':categ_id[0].id,
                  'type':categ_type,
                  'barcode':barcode[0],
                  'uom_id':uom_id,
                  'uom_po_id':uom_po_id,
                  'season_id':season_id,
                  'lst_price':values.get('sale_price'),
                  'standard_price':values.get('cost_price'),
                  'weight':values.get('weight'),
                  'volume':values.get('volume'),
                }
        
        res = product_obj.create(vals)

        return res

    @api.multi
    def import_product(self):
        fp = tempfile.NamedTemporaryFile(delete=False,suffix=".xlsx")
        fp.write(binascii.a2b_base64(self.file))
        fp.seek(0)
        values = {}
        res = {}
        try:
            workbook = xlrd.open_workbook(fp.name)
            sheet = workbook.sheet_by_index(0)
        except Exception:
            raise Warning(_("Please give an Excel File for Importing Products!"))
        for row_no in range(sheet.nrows):
            val = {}
            if row_no <= 0:
                fields = map(lambda row:row.value.encode('utf-8'), sheet.row(row_no))
            else:
                line = list(map(lambda row:isinstance(row.value, bytes) and row.value.encode('utf-8') or str(row.value), sheet.row(row_no)))
                if self.product_option == 'create':
                    values.update( {'name':line[0],
                                        'default_code': line[1],
                                        'categ_id': line[2],
                                        'type': line[3],
                                        'barcode': line[4],
                                        'uom_id': line[5],
                                        'uom_po_id': line[6],
                                        
                                        'cost_price': line[7],
                                        'sale_price': line[8],
                                        'x_studio_vxm_imp': line[9],

                                        'weight': line[10],
                                        'volume': line[11],
                                        #Addional Fields
                                        'season_id': line[12],
                                        'x_studio_color_1': line[13],
                                        
                                        'x_studio_origen': line[14],
                                        'x_studio_hs': line[15],
                                        'x_studio_genero': line[16],
                                        'x_studio_material': line[17]

                                        })
                 
                    res = self.create_product(values)
                else:
                    product_obj = self.env['product.product']
                    product_categ_obj = self.env['product.category']
                    product_uom_obj = self.env['uom.uom']
                    product_season_obj = self.env['product.season']
                    categ_id = False
                    categ_type = False
                    barcode = False
                    uom_id = False
                    uom_po_id = False
                    x_studio_vxm_imp = False
                    season_id = False
                    x_studio_color_1 = False
                    x_studio_origen = False
                    x_studio_hs = False
                    x_studio_genero = False
                    x_studio_material = False
                                        

                    
                    if line[2]=='':
                        pass
                    else:
                        categ_id = product_categ_obj.search([('name','=',line[2])],limit=1)
                        if not categ_id:
                            raise Warning(_('Category %s not found.' %line[2] ))
                    if line[3]=='':
                        pass
                    else:
                        if line[3] == 'Consumable':
                            categ_type ='consu'
                        elif line[3] == 'Service':
                            categ_type ='service'
                        elif line[3] == 'Stockable Product':
                            categ_type ='product'
                        else:
                            categ_type = 'product'
                            
                    if line[4]=='':                             
                        pass
                    else:
                        barcode = line[4].split(".")
                    
                    if line[5]=='':
                        pass
                    else:
                        uom_search_id  = product_uom_obj.search([('name','=',line[5])])
                        if not uom_search_id:
                            raise Warning(_('UOM %s not found.' %line[5]))
                        else:
                            uom_id = uom_search_id.id
                    
                    if line[6]=='':
                        pass
                    else:
                        uom_po_search_id  = product_uom_obj.search([('name','=',line[6])])
                        if not uom_po_search_id:
                            raise Warning(_('Purchase UOM %s not found' %line[6]))
                        else:
                            uom_po_id = uom_po_search_id.id
                    #season

                    if line[12]=='':
                        pass
                    else:
                        season_id = product_season_obj.search([('name','=',line[12])],limit=1)
                        if not season_id:
                            raise Warning(_('Temporada %s no encontrada.' %line[12] ))

                        
                    if self.product_search == 'by_code':
                        if not line[1]:
                            raise Warning(_('Por favor, suministrar Referencia para actualizar.'))

                        product_ids = self.env['product.template'].search([('default_code','=', line[1])],limit=1)
                        if product_ids:
                            if categ_id != False:
                                product_ids.write({'categ_id': categ_id[0].id or False})
                            if categ_type != False:
                                product_ids.write({'type': categ_type or False})
                            if barcode != False:
                                product_ids.write({'barcode': barcode[0] or False})
                            if uom_id != False:
                                product_ids.write({'uom_id': uom_id or False})
                            if uom_po_id != False:
                                product_ids.write({'uom_po_id': uom_po_id})
                            if line[7]:
                                product_ids.write({'lst_price': line[7] or False})
                            if line[8]:
                                product_ids.write({'standard_price': line[8] or False})
                            if line[9]:
                                product_ids.write({'weight': line[9] or False})
                            if line[10]:
                                product_ids.write({'volume': line[10] or False})
                        else:
                            raise Warning(_('"%s" Product not found.') % line[1]) 
                    elif self.product_search == 'by_name':
                        if not line[0]:
                            raise Warning(_('Por favor, suministrar Nombre para actualizar. '))

                        product_ids = self.env['product.template'].search([('name','=', line[0])],limit=1)
                        if product_ids:
                            if categ_id != False:
                                product_ids.write({'categ_id': categ_id[0].id or False})
                            if categ_type != False:
                                product_ids.write({'type': categ_type or False})
                            if barcode != False:
                                product_ids.write({'barcode': barcode[0] or False})
                            if uom_id != False:
                                product_ids.write({'uom_id': uom_id or False})
                            if uom_po_id != False:
                                product_ids.write({'uom_po_id': uom_po_id})
                            if line[7]:
                                product_ids.write({'lst_price': line[7] or False})
                            if line[8]:
                                product_ids.write({'standard_price': line[8] or False})
                            if line[9]:
                                product_ids.write({'weight': line[9] or False})
                            if line[10]:
                                product_ids.write({'volume': line[10] or False})
                        else:
                            raise Warning(_('%s producto no encontrado.') % line[0])  
                    else:
                        if not barcode:
                            raise Warning(_('Por favor, suministrar Código de Barra para actualizar.'))
#BARCODE FILTER
                        product_ids = self.env['product.template'].search([('barcode','=',barcode[0])],limit=1)
                        if product_ids:
                            if categ_id != False:
                                product_ids.write({'categ_id': categ_id[0].id or False})
                            if categ_type != False:
                                product_ids.write({'type': categ_type or False})
                            if uom_id != False:
                                product_ids.write({'uom_id': uom_id or False})
                            if uom_po_id != False:
                                product_ids.write({'uom_po_id': uom_po_id})
                            if line[7]:
                                product_ids.write({'standard_price': line[7] or False})
                            if line[8]:
                                product_ids.write({'lst_price': line[8] or False})
                            if line[9]:
                                product_ids.write({'x_studio_vxm_imp': line[9] or False})      
                            if line[10]:
                                product_ids.write({'weight': line[10] or False})
                            if line[11]:
                                product_ids.write({'volume': line[11] or False})

                            if line[12]:
                                product_ids.write({'season_id': season_id})    
                            if line[13]:
                                product_ids.write({'x_studio_color_1': line[13] or False})    
                            if line[14]:
                                product_ids.write({'x_studio_origen': line[14] or False})
                            if line[15]:
                                product_ids.write({'x_studio_hs': line[15] or False})
                            if line[16]:
                                product_ids.write({'x_studio_genero': line[16] or False})    
                            if line[17]:
                                product_ids.write({'x_studio_material': line[17] or False})   
                            if line[18]:
                                product_ids.write({'x_studio_familia': line[18] or False})
        
    
    

    
                        else:
                            raise Warning(_('%s producto no encontrado.') % line[4])  
        return res

