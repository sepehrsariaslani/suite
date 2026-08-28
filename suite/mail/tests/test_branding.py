# Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from unittest.mock import patch
from email.header import decode_header, make_header
from email.utils import parseaddr

import frappe
from frappe.tests import IntegrationTestCase

from suite.mail.branding import MailBranding, get_mail_branding, get_transactional_sender


class TestMailBranding(IntegrationTestCase):
    def setUp(self) -> None:
        super().setUp()
        frappe.clear_document_cache("Mail Settings")

    def tearDown(self) -> None:
        frappe.clear_document_cache("Mail Settings")
        super().tearDown()

    def test_empty_settings_use_payam_yar_defaults(self):
        with self.change_settings(
            "Mail Settings",
            mail_product_name_fa="",
            mail_product_name_en="",
            mail_sender_name="",
        ):
            frappe.clear_document_cache("Mail Settings")
            self.assertEqual(
                get_mail_branding(),
                MailBranding("پیام‌یار", "Payam Yar", "مجموعه دهاتی"),
            )

    def test_configured_branding_is_returned(self):
        with self.change_settings(
            "Mail Settings",
            mail_product_name_fa="نامه‌رسان",
            mail_product_name_en="Mailroom",
            mail_sender_name="دهاتی",
        ):
            frappe.clear_document_cache("Mail Settings")
            self.assertEqual(
                get_mail_branding(),
                MailBranding("نامه‌رسان", "Mailroom", "دهاتی"),
            )

    @patch("suite.mail.branding.EmailAccount.find_default_outgoing")
    def test_sender_uses_configured_name_and_default_outgoing_address(self, find_default):
        find_default.return_value.email_id = "info@dehati.ir"

        with self.change_settings("Mail Settings", mail_sender_name="مجموعه دهاتی"):
            frappe.clear_document_cache("Mail Settings")
            sender_name, sender_email = parseaddr(get_transactional_sender())
            self.assertEqual(str(make_header(decode_header(sender_name))), "مجموعه دهاتی")
            self.assertEqual(sender_email, "info@dehati.ir")

    @patch("suite.mail.branding.EmailAccount.find_default_outgoing", return_value=None)
    def test_sender_is_empty_without_outgoing_account(self, _find_default):
        self.assertEqual(get_transactional_sender(), "")
