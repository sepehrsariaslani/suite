import unittest
from unittest import mock

from suite.mail import install


class MailInstallTest(unittest.TestCase):
    def test_add_rate_limits_skips_when_doctype_is_unavailable(self):
        with (
            mock.patch.object(install.frappe.db, 'exists', return_value=False),
            mock.patch.object(install, 'create_rate_limit') as create_rate_limit,
            mock.patch.object(install.frappe, 'logger'),
        ):
            install.add_rate_limits()

        create_rate_limit.assert_not_called()
