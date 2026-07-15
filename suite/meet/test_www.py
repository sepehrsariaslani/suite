# Copyright (c) 2026, Frappe and contributors
# For license information, please see license.txt

import frappe
from frappe.tests import IntegrationTestCase

from suite.meet.utils.sfu_config import get_sfu_config
from suite.meet.www.meet import get_boot


class IntegrationTestMeetWww(IntegrationTestCase):
	def test_get_boot_marks_sfu_disabled_without_secret(self):
		original_secret = frappe.conf.get("sfu_secret")
		original_url = frappe.conf.get("sfu_server_url")

		try:
			frappe.conf.sfu_secret = ""
			frappe.conf.sfu_server_url = "https://sfu.example.test"
			get_sfu_config.clear_cache()

			boot = get_boot()

			self.assertFalse(boot["sfu_enabled"])
		finally:
			get_sfu_config.clear_cache()
			frappe.conf.sfu_secret = original_secret
			frappe.conf.sfu_server_url = original_url

	def test_get_boot_marks_sfu_enabled_when_secret_and_url_exist(self):
		original_secret = frappe.conf.get("sfu_secret")
		original_url = frappe.conf.get("sfu_server_url")

		try:
			frappe.conf.sfu_secret = "test-sfu-secret"
			frappe.conf.sfu_server_url = "https://sfu.example.test"
			get_sfu_config.clear_cache()

			boot = get_boot()

			self.assertTrue(boot["sfu_enabled"])
		finally:
			get_sfu_config.clear_cache()
			frappe.conf.sfu_secret = original_secret
			frappe.conf.sfu_server_url = original_url
