# See LICENSE file for full copyright and licensing details.

from odoo import models, fields


class PosConfig(models.Model):

    _inherit = "pos.config"

    disable_discount = fields.Boolean('Hide Discount')
