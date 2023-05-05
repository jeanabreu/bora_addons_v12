###################################################################################
# 
#    Copyright (C) Cetmix OÜ
#
#   Odoo Proprietary License v1.0
# 
#   This software and associated files (the "Software") may only be used (executed,
#   modified, executed after modifications) if you have purchased a valid license
#   from the authors, typically via Odoo Apps, or if you have received a written
#   agreement from the authors of the Software (see the COPYRIGHT file).
# 
#   You may develop Odoo modules that use the Software as a library (typically
#   by depending on it, importing it and using its resources), but without copying
#   any source code or material from the Software. You may distribute those
#   modules under the license of your choice, provided that this license is
#   compatible with the terms of the Odoo Proprietary License (For example:
#   LGPL, MIT, or proprietary licenses similar to this one).
# 
#   It is forbidden to publish, distribute, sublicense, or sell copies of the Software
#   or modified copies of the Software.
# 
#   The above copyright notice and this permission notice must be included in all
#   copies or substantial portions of the Software.
# 
#   THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#   IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#   FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
#   IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
#   DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
#   ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
#   DEALINGS IN THE SOFTWARE.
#
###################################################################################

from odoo import models, fields, api, _
from datetime import timezone
import pytz

import logging
_logger = logging.getLogger(__name__)


# -- Select draft
def _select_draft(draft):
    if draft:
        return {
            'name': _("New message"),
            "views": [[False, "form"]],
            'res_model': 'mail.compose.message',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': {
                'default_res_id': draft.res_id,
                'default_model': draft.model,
                'default_parent_id': draft.parent_id,
                'default_partner_ids': draft.partner_ids.ids or False,
                'default_attachment_ids': draft.attachment_ids.ids or False,
                'default_is_log': False,
                'default_subject': draft.subject,
                'default_body': draft.body,
                'default_subtype_id': draft.subtype_id.id,
                'default_message_type': 'comment',
                'default_current_draft_id': draft.id,
                'default_signature_location': draft.signature_location,
                'default_wizard_mode': draft.wizard_mode
                }
        }


######################
# Mail.Message.Draft #
######################
class PRTMailMessageDraftPro(models.Model):
    _name = "prt.mail.message.draft"
    _inherit = ['prt.mail.message.draft', 'mail.thread', 'mail.activity.mixin']

    label = fields.Char(string="Draft Label")

# -- Open record selection wizard
    @api.multi
    def select_record(self):
        self.ensure_one()

        return {
            'name': _("Select record"),
            "views": [[False, "form"]],
            'res_model': 'prt.message.draft.ref',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': {
                'default_draft_id': self.id,
            }
        }

# -- Name get. Override if choosing draft from wizard
    @api.multi
    def name_get(self):

        if self._context.get('draft2wiz', False):

            # Get from context and force to UTC if False
            tz = self._context.get('tz', 'Etc/UTC')
            if not tz:
                tz = 'Etc/UTC'

            user_tz = pytz.timezone(tz)

            x = len(self)
            res = []
            for rec in self:
                if rec.label:
                    res.append((rec.id, _("Version #%s: %s edited by %s") % (str(x), rec.label, rec.write_uid.name)))
                else:
                    res.append((rec.id, _("Version #%s from %s edited by %s") % (str(x), str(rec.write_date.replace(tzinfo=timezone.utc).astimezone(tz=user_tz))[:19], rec.write_uid.name)))
                x -= 1
            return res

        return super().name_get()

# -- Override Get Subject for tree view
    @api.depends('subject')
    @api.multi
    def _subject_display(self):

        # Get model names first. Use this method to get translated values
        ir_models = self.env['ir.model'].search([('model', 'in', list(set(self.mapped('model'))))])
        model_dict = {}
        for model in ir_models:
            # Check if model has "name" field
            has_name = self.env['ir.model.fields'].sudo().search_count([('model_id', '=', model.id),
                                                                        ('name', '=', 'name')])
            model_dict.update({model.model: [model.name, has_name]})

        # Compose subject
        for rec in self:
            subject_display = '=== No Reference ==='

            # Has reference
            if rec.record_ref:
                subject_display = model_dict.get(rec.model)[0]

                # Has 'name' field
                if model_dict.get(rec.model, False)[1]:
                    subject_display = "%s: %s" % (subject_display, rec.record_ref.name)

                # Has subject
                if rec.subject:
                    subject_display = "%s => %s" % (subject_display, rec.subject)

                # Has label
                if rec.label:
                    subject_display = "%s # %s" % (subject_display, rec.label)

            # Set subject
            rec.subject_display = subject_display


############################
# Mail Draft Select Record #
############################
class PRTMailMove(models.TransientModel):
    _name = 'prt.message.draft.ref'
    _description = 'Select Record Ref for Draft Message'

    record_ref = fields.Reference(string="Select record", selection='_referenceable_models')
    draft_id = fields.Integer(string="Message")

# -- Ref models
    @api.model
    def _referenceable_models(self):
        return [(x.model, x.name) for x in self.env['ir.model'].sudo().search([('is_mail_thread', '=', True),
                                                                               ('model', '!=', 'mail.thread')])]

# -- Set reference
    def set_ref(self):
        self.ensure_one()
        if not self.draft_id:
            return
        if not self.record_ref:
            return

        self.env['prt.mail.message.draft'].browse(self.draft_id).sudo().write({
            'model': self.record_ref._name,
            'res_id': self.record_ref.id
        })


########################
# Mail.Compose Message #
########################
class PRTMailComposer(models.TransientModel):
    _inherit = 'mail.compose.message'
    _name = 'mail.compose.message'

    draft_count = fields.Integer(string="", compute="_draft_count")

# -- Count drafts
    @api.depends('model', 'res_id')
    @api.multi
    def _draft_count(self):
        self.ensure_one()
        dc = self.env['prt.mail.message.draft'].search_count([('model', '=', self.model),
                                                              ('res_id', '=', self.res_id)])
        if self.current_draft_id:
            dc -= 1
        self.draft_count = dc

# -- Restore draft
    @api.multi
    def restore_draft(self):
        self.ensure_one()

        # Save current draft
        draft_id = self.current_draft_id if self.current_draft_id else False
        res = self._save_draft(draft_id)

        # Open draft selection wizard
        return {'type': 'ir.actions.act_window',
                'name': _("Restore from draft"),
                'view_mode': 'form',
                'view_type': 'form',
                'res_model': 'prt.message.draft.ver',
                'target': 'new',
                'context': {
                    'default_current_draft_id': draft_id.id if draft_id else res.id,
                    'default_model': self.model,
                    'default_res_id': self.res_id
                },
                }


#####################################
# Mail Compose Message Select Draft #
#####################################
class PRTMailDraftSelect(models.TransientModel):
    _name = 'prt.message.draft.ver'
    _description = 'Select Draft Message'

    current_draft_id = fields.Many2one(string="Draft version", comodel_name='prt.mail.message.draft')
    draft_id = fields.Many2one(string="Draft version", comodel_name='prt.mail.message.draft',
                               context={'draft2wiz': True},
                               help="Will restore values from draft selected\n"
                                    "Current draft will be saved")

    subject = fields.Char(string="Subject", related='draft_id.subject', readonly="1")
    body = fields.Html(string="Body", related='draft_id.body', readonly="1")
    model = fields.Char(sting="Related Document Model")
    res_id = fields.Integer(string="Related Document ID")

# -- Select draft wrapper
    @api.multi
    def select_draft(self):
        self.ensure_one()
        if self.draft_id:
            return _select_draft(self.draft_id)

# -- Restore previous draft
    @api.multi
    def previous_draft(self):
        self.ensure_one()
        if self.current_draft_id:
            return _select_draft(self.current_draft_id)
