# Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from unittest.mock import patch
import frappe
from frappe.tests import IntegrationTestCase

from suite.mail.branding import MailBranding, get_mail_branding, get_transactional_sender
from suite.mail.doctype.mail_account_request.mail_account_request import MailAccountRequest


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
            self.assertEqual(get_transactional_sender(), "مجموعه دهاتی <info@dehati.ir>")

    @patch("suite.mail.branding.EmailAccount.find_default_outgoing", return_value=None)
    def test_sender_is_empty_without_outgoing_account(self, _find_default):
        self.assertEqual(get_transactional_sender(), "")


class TestPayamYarAccountEmail(IntegrationTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.request = frappe.new_doc("Mail Account Request")
        self.request.account = "new-member@dehati.ir"
        self.request.backup_email = "recipient@example.test"
        self.request.invited_by = "Administrator"
        self.request.request_key = "test-request-key"

    @patch(
        "suite.mail.doctype.mail_account_request.mail_account_request.get_transactional_sender",
        return_value="encoded-sender <info@dehati.ir>",
    )
    @patch("suite.mail.doctype.mail_account_request.mail_account_request.is_system_manager", return_value=False)
    @patch("suite.mail.doctype.mail_account_request.mail_account_request.is_suite_admin", return_value=False)
    @patch("frappe.sendmail")
    def test_invitation_email_uses_payam_yar_branding(
        self, sendmail, _is_suite_admin, _is_system_manager, _get_sender
    ):
        self.request._send_invite_email()

        kwargs = sendmail.call_args.kwargs
        self.assertEqual(kwargs["recipients"], "recipient@example.test")
        self.assertEqual(kwargs["sender"], "encoded-sender <info@dehati.ir>")
        self.assertEqual(kwargs["subject"], "دعوت‌نامه عضویت در پیام‌یار")
        self.assertEqual(kwargs["template"], "payam_yar_account_email")
        self.assertTrue(kwargs["now"])
        self.assertEqual(kwargs["args"]["direction"], "rtl")
        self.assertEqual(kwargs["args"]["button_label"], "تأیید و ساخت حساب")
        self.assertTrue(kwargs["args"]["action_url"].endswith("/mail/signup/test-request-key"))

    @patch(
        "suite.mail.doctype.mail_account_request.mail_account_request.get_transactional_sender",
        return_value="encoded-sender <info@dehati.ir>",
    )
    @patch("frappe.sendmail")
    def test_otp_email_uses_payam_yar_branding(self, sendmail, _get_sender):
        self.request._signup_otp = "123456"

        self.request._send_otp_email()

        kwargs = sendmail.call_args.kwargs
        self.assertEqual(kwargs["recipients"], "recipient@example.test")
        self.assertEqual(kwargs["sender"], "encoded-sender <info@dehati.ir>")
        self.assertEqual(kwargs["subject"], "کد تأیید پیام‌یار")
        self.assertEqual(kwargs["template"], "payam_yar_account_email")
        self.assertEqual(kwargs["args"]["verification_code"], "123456")
        self.assertEqual(kwargs["args"]["expiry_minutes"], 10)
        self.assertIsNone(self.request._signup_otp)
