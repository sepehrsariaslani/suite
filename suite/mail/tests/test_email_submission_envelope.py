# Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt
"""Wire format of the JMAP submission envelope."""

import unittest
from unittest import mock

from suite.mail.jmap.services.mail.submission.email_submission import EmailSubmissionService


class TestBuildEnvelope(unittest.TestCase):
    def _envelope(self, hold_until: int | None = None) -> dict:
        return EmailSubmissionService._build_envelope(
            from_email="sender@example.com",
            rcpt_emails=["rcpt@example.com"],
            envelope_id="env-1",
            priority=0,
            hold_until=hold_until,
        )

    @mock.patch(
        "suite.mail.jmap.services.mail.submission.email_submission.time",
        return_value=1767270000,
    )
    def test_hold_until_uses_relative_hold_for(self, _time):
        parameters = self._envelope(hold_until=1767270896)["mailFrom"]["parameters"]
        self.assertEqual(parameters.get("HOLDFOR"), "896")
        self.assertNotIn("HOLDUNTIL", parameters)

    def test_no_hold_until_omits_parameter(self):
        parameters = self._envelope()["mailFrom"]["parameters"]
        self.assertNotIn("HOLDUNTIL", parameters)
