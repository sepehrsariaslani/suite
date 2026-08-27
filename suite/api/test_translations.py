import unittest
from unittest import mock

from suite import api


class TranslationApiTest(unittest.TestCase):
    def test_returns_logged_in_user_language_and_rtl_direction(self):
        frappe = mock.Mock()
        frappe.session.user = "user@example.com"
        frappe.db.get_value.return_value = "fa"
        frappe.whitelist = lambda **kwargs: lambda fn: fn

        with (
            mock.patch.object(api, "frappe", frappe, create=True),
            mock.patch.object(api, "get_all_translations", return_value={"Settings": "تنظیمات"}, create=True),
        ):
            result = api.get_translations()

        self.assertEqual(result["language"], "fa")
        self.assertEqual(result["direction"], "rtl")
        self.assertEqual(result["messages"]["Settings"], "تنظیمات")
