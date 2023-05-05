# Copyright 2009 NetAndCo (<http://www.netandco.net>).
# Copyright 2011 Akretion Benoît Guillot <benoit.guillot@akretion.com>
# Copyright 2014 prisnet.ch Seraphine Lantible <s.lantible@gmail.com>
# Copyright 2016 Serpent Consulting Services Pvt. Ltd.
# Copyright 2018 Daniel Campos <danielcampos@avanzosc.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import api, fields, models


class ProductInternalCategory(models.Model):
    _name = 'product.internal_category'
    _description = "Product Internal category"
    _order = 'name'

    name = fields.Char('Internal Category Name', required=True)
    description = fields.Text(translate=True)
    partner_id = fields.Many2one(
        'res.partner',
        string='Partner',
        help='Select a partner for this internal category if any.',
        ondelete='restrict'
    )
    logo = fields.Binary('Logo File', attachment=True)
    product_ids = fields.One2many(
        'product.template',
        'product_internal_category_id',
        string='Internal Category Products',
    )
    products_count = fields.Integer(
        string='Number of products',
        compute='_compute_products_count',
    )

    @api.multi
    @api.depends('product_ids')
    def _compute_products_count(self):
        for internal_category in self:
            internal_category.products_count = len(internal_category.product_ids)


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    product_internal_category_id = fields.Many2one(
        'product.internal_category',
        string='Internal Category',
        index=True,
        help='Select a internal category for this product'
    )
