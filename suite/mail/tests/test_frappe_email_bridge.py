from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import patch

from frappe.tests import UnitTestCase


class TestFrappeEmailBridge(UnitTestCase):
    def test_sync_sent_queue_imports_once_and_marks_the_mirror_synced(self):
        from suite.mail import frappe_email_bridge

        queue = SimpleNamespace(name="QUEUE-001", status="Sent", email_account="Dehati Mail")
        mirror = SimpleNamespace(status="Pending", attempts=0, jmap_email_id=None)

        with (
            patch.object(frappe_email_bridge.frappe, "get_doc", return_value=queue),
            patch.object(frappe_email_bridge, "_get_or_create_mirror", return_value=mirror),
            patch.object(frappe_email_bridge, "_resolve_jmap_account", return_value="c"),
            patch.object(frappe_email_bridge, "_import_queue_into_sent", return_value="jmap-email-1") as importer,
            patch.object(frappe_email_bridge, "_mark_synced") as mark_synced,
        ):
            result = frappe_email_bridge.sync_sent_email_queue("QUEUE-001")

        importer.assert_called_once_with(queue, "c")
        mark_synced.assert_called_once_with(mirror, "c", "jmap-email-1")
        self.assertEqual(result, {"queue_name": "QUEUE-001", "state": "synced", "jmap_email_id": "jmap-email-1"})

    def test_sync_does_not_import_an_already_synced_queue_again(self):
        from suite.mail import frappe_email_bridge

        queue = SimpleNamespace(name="QUEUE-002", status="Sent", email_account="Dehati Mail")
        mirror = SimpleNamespace(status="Synced", attempts=1, jmap_email_id="jmap-email-2")

        with (
            patch.object(frappe_email_bridge.frappe, "get_doc", return_value=queue),
            patch.object(frappe_email_bridge, "_get_or_create_mirror", return_value=mirror),
            patch.object(frappe_email_bridge, "_import_queue_into_sent") as importer,
        ):
            result = frappe_email_bridge.sync_sent_email_queue("QUEUE-002")

        importer.assert_not_called()
        self.assertEqual(result, {"queue_name": "QUEUE-002", "state": "already_synced", "jmap_email_id": "jmap-email-2"})

    def test_queue_message_preserves_the_mime_body_and_replaces_frappe_recipient_placeholder(self):
        from suite.mail import frappe_email_bridge

        queue = SimpleNamespace(
            name="QUEUE-003",
            message="From: Dehati <info@dehati.ir>\r\nTo: <!--recipient-->\r\nSubject: Report\r\n\r\nBody",
            recipients=[SimpleNamespace(recipient="recipient@example.com")],
        )

        message = frappe_email_bridge._queue_message(queue).decode("utf-8")

        self.assertIn("To: recipient@example.com", message)
        self.assertIn("X-Frappe-Email-Queue: QUEUE-003", message)
        self.assertIn("\r\n\r\nBody", message)
