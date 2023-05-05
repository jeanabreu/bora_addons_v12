# -*- coding: utf-8 -*-

from openerp import api, fields, models, _


class MergeProducts(models.Model):
    _name = "merge.product"
    _description = 'Merge Products'

    @api.model
    def select_all_product_models(self):
        models_to_skip = ['product.template', 'product.product', 'merge.product.line', 'merge.product.history']
        Fields = self.env['ir.model.fields']
        field_ids = Fields.search([('ttype', '=', 'many2one'), ('relation', '=', 'product.product'),
                                       ('model_id.model', 'not in', models_to_skip),
                                       ('model_id.transient', '=', False), ('related', 'in', (False, ''))])
        model_ids = [model.id for model in field_ids.mapped('model_id') if self.env[model.model]._auto == True]
        return [(6, 0, set(model_ids))]

    name = fields.Char('Reference', copy=False, default='/')
    product_line_ids = fields.One2many('merge.product.line', 'product_merge_id', 'Product Lines')
    model_ids = fields.Many2many('ir.model', 'merge_product_model_rel', 'merge_product_id', 'model_id', 'Models',
                                 domain="[('field_id.ttype', '=', 'many2one'), ('field_id.relation', '=', 'product.product')]",
                                 default=select_all_product_models, required=True)
    state = fields.Selection([('draft', 'Draft'), ('finish', 'Finished'), ('cancel', 'Cancelled')], string='State',
                             default='draft', copy=False)

    @api.multi
    def deselect_all_product_models(self):
        self.ensure_one()
        self.model_ids = [(6, 0, [])]
        return True

    @api.multi
    def get_product_fields(self):
        self.ensure_one()
        Fields = self.env['ir.model.fields']
        model_dict = {}
        for model_brw in self.model_ids:
            product_field = False
            product_tmpl_field = False
            field_ids = Fields.search([('ttype', '=', 'many2one'), ('relation', '=', 'product.product'),
                                          ('model_id.model', '=', model_brw.model), ('related', 'in', (False, ''))])
            if field_ids:
                product_field = field_ids[0].name

            tmpl_field_ids = Fields.search([('ttype', '=', 'many2one'), ('relation', '=', 'product.template'),
                                               ('model_id.model', '=', model_brw.model), ('related', 'in', (False, ''))])
            if tmpl_field_ids:
                product_tmpl_field = tmpl_field_ids[0].name
            model_dict[model_brw] = (product_field, product_tmpl_field)

        return model_dict

    def get_history_line_vals(self, model, model_rec_ids):
        rec_name = model_rec_ids._rec_name
        vals = {
            'model_id': model.id,
            'record_ids_note': sorted(model_rec_ids.mapped('id'))
        }
        if rec_name:
            if getattr(model_rec_ids[0], rec_name):
                vals.update({'note': ', '.join(map(str, model_rec_ids.sorted(lambda rec:rec.id).mapped(rec_name)))})
        else:
            vals.update({'note': model_rec_ids.mapped('id')})
        return vals

    @api.multi
    def action_merge_products(self):
        self.ensure_one()
        model_dict = self.get_product_fields()
        for line in self.product_line_ids:
            remove_product = line.remove_product_id
            new_product = line.new_product_id
            if remove_product.id == new_product.id:
                continue
            history_lines = []
            for model in model_dict:
                Model = self.env[model.model]
                model_search_ids = Model.search([(model_dict[model][0], '=', remove_product.id)])
                if model_search_ids:
                    vals = {model_dict[model][0]: new_product.id}
                    if model_dict.get(model)[1]:
                        vals.update({model_dict[model][1]: new_product.product_tmpl_id.id})
                    model_search_ids.write(vals)
                    history = self.get_history_line_vals(model, model_search_ids)
                    history_lines.append((0, 0, history))
                else:
                    history_lines.append((0, 0, {'model_id': model.id,
                                                 'note': 'No Records Found!'}))
            if history_lines:
                line.write({'history_ids': history_lines})
        return self.write({'state': 'finish', 'name': self.env['ir.sequence'].next_by_code('seq.merge.products')})

    @api.multi
    def action_cancel(self):
        self.write({'state':'cancel'})

class MergeProductLine(models.Model):
    _name = "merge.product.line"

    product_merge_id = fields.Many2one('merge.product', 'Merge Product', ondelete='cascade', copy=False, required=True)
    remove_product_id = fields.Many2one('product.product', 'Product to Remove', domain="[('id', '!=', new_product_id)]", copy=False, required=True)
    product_type = fields.Selection([('consu', 'Consumable'), ('service', 'Service'), ('product', 'Storable')],
                                    related='remove_product_id.type')
    new_product_id = fields.Many2one('product.product', string='Replace With Product',
                                     domain="[('id', '!=', remove_product_id)]", copy=False, required=True)
    history_ids = fields.One2many('merge.product.history', 'product_line_id', 'History', copy=False)

    @api.onchange('remove_product_id')
    def onchange_remove_product(self):
        self.new_product_id = False

class MergeProductHistory(models.Model):
    _name = "merge.product.history"

    product_line_id = fields.Many2one('merge.product.line', 'Merge Product Line', readonly=True, ondelete='cascade', copy=False)
    model_id = fields.Many2one('ir.model', 'Model', readonly=True, copy=False)
    note = fields.Text('Records Affected', copy=False)
    record_ids_note = fields.Text('Record IDs', copy=False)
