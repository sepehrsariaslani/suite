from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import patch

from frappe.tests import UnitTestCase
from frappe.model.base_document import import_controller

from suite.mail import mcp_api


class TestMcpEmailApi(UnitTestCase):
    def test_idempotency_doctype_uses_the_resolvable_controller_name(self):
        controller = import_controller("Suite MCP Email Request")

        self.assertEqual(controller.__name__, "SuiteMCPEmailRequest")

    def test_prepare_email_returns_exact_sender_without_internal_queue_attachment_data(self):
        account = SimpleNamespace(name="Dehati Mail")
        with (
            patch.object(mcp_api, "_require_system_manager"),
            patch.object(mcp_api, "_outgoing_account", return_value=("info@dehati.ir", account)),
            patch.object(mcp_api, "_attachments", return_value=([], [])),
            patch.object(mcp_api, "_reference", return_value=(None, None)),
        ):
            result = mcp_api.prepare_email(
                sender="info@dehati.ir",
                email_account="Dehati Mail",
                recipients=["recipient@example.com"],
                subject="Weekly report",
                message="Preview only",
            )

        self.assertEqual(result["preview"]["sender"], "info@dehati.ir")
        self.assertEqual(result["preview"]["email_account"], "Dehati Mail")
        self.assertNotIn("attachment_queue_rows", result["preview"])
        self.assertTrue(result["confirmation"]["preview_fingerprint"])

    def test_outgoing_account_rejects_disabled_or_mismatched_sender(self):
        disabled = SimpleNamespace(enable_outgoing=0, email_id="info@dehati.ir")
        with patch.object(mcp_api.frappe, "get_doc", return_value=disabled):
            with self.assertRaises(mcp_api.frappe.PermissionError):
                mcp_api._outgoing_account("info@dehati.ir", "Dehati Mail")

    def test_prepare_email_sanitizes_html_and_marks_rtl_content(self):
        account = SimpleNamespace(name="Dehati Mail")
        with (
            patch.object(mcp_api, "_require_system_manager"),
            patch.object(mcp_api, "_outgoing_account", return_value=("info@dehati.ir", account)),
            patch.object(mcp_api, "_attachments", return_value=([], [])),
            patch.object(mcp_api, "_reference", return_value=(None, None)),
        ):
            result = mcp_api.prepare_email(
                sender="info@dehati.ir",
                email_account="Dehati Mail",
                recipients=["recipient@example.com"],
                subject="گزارش فروش",
                message='<p>گزارش فروش</p><script>alert("x")</script>',
            )

        self.assertNotIn("<script", result["preview"]["message"].lower())
        self.assertIn('dir="rtl"', result["preview"]["message"])

    def test_email_status_alias_and_queue_search_return_safe_fields(self):
        row = SimpleNamespace(
            name="QUEUE-1",
            status="Not Sent",
            retry=0,
            sender="info@dehati.ir",
            email_account="Dehati Mail",
            creation="2026-09-05 12:00:00",
            modified="2026-09-05 12:00:00",
            error="",
        )
        with (
            patch.object(mcp_api, "_require_system_manager"),
            patch.object(mcp_api.frappe, "get_doc", return_value=row),
            patch.object(mcp_api.frappe, "get_all", return_value=[row]),
        ):
            status = mcp_api.get_email_status("QUEUE-1")
            queued = mcp_api.search_email_queue(status="Not Sent", limit=10)

        self.assertEqual(status["queue"]["name"], "QUEUE-1")
        self.assertEqual(queued["queues"][0]["sender"], "info@dehati.ir")
        self.assertNotIn("error", queued["queues"][0])
