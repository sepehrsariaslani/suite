# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and Contributors
# See license.txt

# import frappe
from unittest.mock import patch

from frappe.tests import IntegrationTestCase, UnitTestCase

from suite.mail import install as mail_install

# On IntegrationTestCase, the doctype test records and all
# link-field test record dependencies are recursively loaded
# Use these module variables to add/remove to/from that list
EXTRA_TEST_RECORD_DEPENDENCIES = []  # eg. ["User"]
IGNORE_TEST_RECORD_DEPENDENCIES = []  # eg. ["User"]


class UnitTestRateLimit(UnitTestCase):
	"""
	Unit tests for RateLimit.
	Use this class for testing individual functions and methods.
	"""

	def test_add_rate_limits_skips_when_doctype_is_unavailable(self):
		with (
			patch.object(mail_install.frappe.db, "exists", return_value=False),
			patch.object(mail_install, "create_rate_limit") as create_rate_limit,
			patch.object(mail_install.frappe, "logger"),
		):
			mail_install.add_rate_limits()

		create_rate_limit.assert_not_called()


class IntegrationTestRateLimit(IntegrationTestCase):
	"""
	Integration tests for RateLimit.
	Use this class for testing interactions between multiple components.
	"""

	pass
