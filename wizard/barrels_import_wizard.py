# -*- coding:utf-8 -*-
import base64
from tempfile import TemporaryFile
from openerp import models, fields, api, _
import csv 
from openerp.exceptions import ValidationError
import logging
_logger = logging.getLogger(__name__)

class ImportStockInventory(models.TransientModel):
    _name = 'import.barrels.inventory'

    import_file = fields.Binary(string="Import Excel File", redonly=True)
    datas_fname = fields.Char('Import File Name')
    
    location_id = fields.Many2one('stock.location',
        string='Location', 
        help="Select the owner for those barrels. ")
    
    owner_id = fields.Many2one( 'res.partner', 
        string="Owner", 
        help="Select the owner for those barrels. ")
    
    @api.multi
    def action_import_file(self):
        active_id = self._context.get('active_id')
        active_model = self._context.get('active_model')
        stock_id = self.env[active_model].browse(active_id)
        product_obj = self.env['product.product']
        product_uom_obj = self.env['product.uom']
        product_lot_obj = self.env['stock.production.lot']
        stock_inv_line_obj = self.env['stock.inventory.line']
        ctx = self.env.context
        if self.location_id:
            location_id = self.location_id.id
        elif 'active_id' in ctx:
            inventory_obj = self.env['stock.inventory']
            inventory = inventory_obj.browse(ctx['active_id'])
            location_id = inventory.location_id and inventory.location_id.id or False

        if self.datas_fname[-4:] == '.csv':
            fileobj = TemporaryFile('w+')
            fileobj.write(base64.decodestring(self.import_file))
            fileobj.seek(0)
            reader = csv.reader(fileobj, quotechar='"', delimiter=',')
            count = 1
            lines = []
            missing_product = []
            for row in reader:
                _logger.info(u"line %s - Serial number = %s"% (count,row[3]))
                if count == 1:
                    count += 1
                    continue
                count += 1
                product = product_obj.search([('default_code','=',row[0])])
                if product:
                    line_vals = {
                            'product_id':product.id,
                            'product_qty':row[1],
                            'inventory_id':stock_id.id,
                            'location_id': location_id,
                        }
                    if row[2]:
                        uom = product_uom_obj.search([('name','=',row[2])])
                        if uom:
                            line_vals.update({'product_uom_id':uom.id})
                # row 3 = serial
                    if row[3]:
                        lot = product_lot_obj.search([('name','=',row[3])])
                        if not lot:
                            serial_vals = {
                            'product_id':product.id,
                            'product_qty':row[1],
                            'name':row[3]
                                }
                            serial_line = product_lot_obj.create(serial_vals)
                            lot = product_lot_obj.search([('name','=',row[3])])
                        if lot:
                            line_vals.update({'prod_lot_id':lot.id})
                # check si le baril existe ailleur
                    lines.append(line_vals)
                else:
                    missing_product.append(row[0])
            if not missing_product and lines:
                for line_vals in lines:
                    stock_line = stock_inv_line_obj.create(line_vals)
            else:
                missing_product_name = ',\n'.join(missing_product)
                raise ValidationError(_('Below products are missing in system \n %s.'%missing_product_name))
        else:
            raise ValidationError(_('Wrong file format. Please enter .csv file.'))
