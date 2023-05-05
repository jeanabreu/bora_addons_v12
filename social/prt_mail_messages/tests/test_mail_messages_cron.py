###################################################################################
# 
#    Copyright (C) Cetmix OÜ
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU LESSER GENERAL PUBLIC LICENSE as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###################################################################################

from datetime import timedelta

from odoo import fields
from odoo.tests import common


class TestPrtMailMessage(common.TransactionCase):
    def setUp(self):
        super(TestPrtMailMessage, self).setUp()

    def test_conversation(self):
        Conversation = self.env["cetmix.conversation"]
        conversation_object = Conversation.create(
            {
                "active": True,
                "name": "Test Conversation",
                "author_id": self.env["res.partner"]
                .create({"name": "Test Author #1", "email": "test.author@exapmle.com"})
                .id,
            }
        )

        conversation_message_1 = (
            self.env["mail.message"]
            .sudo(self.env.user)
            .create(
                {
                    "res_id": conversation_object.id,
                    "model": "cetmix.conversation",
                    "reply_to": "test.reply@example.com",
                    "email_from": "test.from@example.com",
                    "body": "test1",
                }
            )
        )

        conversation_message_2 = (
            self.env["mail.message"]
            .sudo(self.env.user)
            .create(
                {
                    "res_id": conversation_object.id,
                    "model": "cetmix.conversation",
                    "reply_to": "test.reply@example.com",
                    "email_from": "test.from@example.com",
                    "body": "test2",
                }
            )
        )

        messages = (
            self.env["mail.message"]
            .with_context(active_test=False)
            .search(
                [
                    ("res_id", "=", conversation_object.id),
                    ("message_type", "!=", "notification"),
                ]
            )
        )

        messages.unlink_pro()

        self.assertFalse(conversation_object.active)
        self.assertFalse(conversation_message_1.active)
        self.assertNotEqual(conversation_message_1.delete_uid, False)
        self.assertNotEqual(conversation_message_1.delete_date, False)
        self.assertFalse(conversation_message_2.active)
        self.assertNotEqual(conversation_message_2.delete_uid, False)
        self.assertNotEqual(conversation_message_2.delete_date, False)

        messages = (
            self.env["mail.message"]
            .with_context(active_test=False)
            .search(
                [
                    ("res_id", "=", conversation_object.id),
                    ("message_type", "!=", "notification"),
                ]
            )
        )

        messages.unlink_pro()

        self.assertFalse(Conversation.search([("id", "=", conversation_message_1.id)]))
        self.assertFalse(Conversation.search([("id", "=", conversation_message_2.id)]))

    def test_unarchive_conversation(self):
        Conversation = self.env["cetmix.conversation"]
        conversation_object = Conversation.create(
            {
                "active": True,
                "name": "Test Conversation",
                "author_id": self.env["res.partner"]
                .create({"name": "Test Author #1", "email": "test.author@exapmle.com"})
                .id,
            }
        )

        conversation_message_1 = (
            self.env["mail.message"]
            .sudo(self.env.user)
            .create(
                {
                    "res_id": conversation_object.id,
                    "model": "cetmix.conversation",
                    "reply_to": "test.reply@example.com",
                    "email_from": "test.from@example.com",
                    "body": "test1",
                }
            )
        )

        conversation_message_2 = (
            self.env["mail.message"]
            .sudo(self.env.user)
            .create(
                {
                    "res_id": conversation_object.id,
                    "model": "cetmix.conversation",
                    "reply_to": "test.reply@example.com",
                    "email_from": "test.from@example.com",
                    "body": "test2",
                }
            )
        )

        messages = (
            self.env["mail.message"]
            .with_context(active_test=False)
            .search(
                [
                    ("res_id", "=", conversation_object.id),
                    ("message_type", "!=", "notification"),
                ]
            )
        )

        messages.unlink_pro()

        self.assertFalse(conversation_object.active)
        self.assertFalse(conversation_message_1.active)
        self.assertNotEqual(conversation_message_1.delete_uid, False)
        self.assertNotEqual(conversation_message_1.delete_date, False)
        self.assertFalse(conversation_message_2.active)
        self.assertNotEqual(conversation_message_2.delete_uid, False)
        self.assertNotEqual(conversation_message_2.delete_date, False)

        conversation_message_1.undelete()

        self.assertTrue(conversation_object.active)
        self.assertTrue(conversation_message_1.active)
        self.assertFalse(conversation_message_2.active)

    def test_unlink_trash_message(self):
        self.env["ir.config_parameter"].sudo().set_param(
            "cetmix.messages_easy_empty_trash", 1
        )
        mail_message = self.env["mail.message"].sudo()

        compute_datetime = fields.Datetime.now() - timedelta(days=3)

        self.env["mail.message"].sudo().create(
            {
                "reply_to": "test.reply@example.com",
                "email_from": "test.from@example.com",
                "active": False,
                "delete_uid": self.env.user.id,
                "delete_date": compute_datetime,
            }
        )
        mail_message._unlink_trash_message()
        count_mail_message = (
            self.env["mail.message"]
            .sudo()
            .search([("reply_to", "=", "test.reply@example.com")])
        )
        self.assertEqual(len(count_mail_message), 0)
