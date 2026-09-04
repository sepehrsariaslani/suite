from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import patch

from frappe.tests import UnitTestCase

from suite.mail import mcp_api


class TestMcpEmailApi(UnitTestCase):
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

