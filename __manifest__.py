# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

{
    'name': 'Barrels Inventory Import Using CSV',
    'version': '1.0',
    'author': "Portall Solutions inc.",
    'website': "portall.ca",
    'category': 'Maple',
    'summary':  'Stock Inventory Adjustments Import using CSV',
    'depends': ['stock'],
    'description': """
    This module add import barrels inventory CSV File.
    """,
    'data': [
         'wizard/barrels_import_wizard.xml',
         'views/barrels_import_view.xml',
     ],
    'installable': True,
    'application': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
