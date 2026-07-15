import unittest
from types import SimpleNamespace
from unittest.mock import patch

from suite.drive.api.storage import MEGA_BYTE, storage_breakdown


class _FakeQuery:
	def select(self, *args, **kwargs):
		return self

	def where(self, *args, **kwargs):
		return self

	def groupby(self, *args, **kwargs):
		return self

	def run(self, **kwargs):
		return []


class TestStorageApi(unittest.TestCase):
	@patch("suite.drive.api.storage.get_default_team", return_value="TEAM-1")
	@patch("suite.drive.api.storage.get_teams", return_value=["TEAM-1"])
	@patch("suite.drive.api.storage.frappe.get_value", return_value=200)
	@patch("suite.drive.api.storage.frappe.db.get_list", return_value=[])
	@patch("suite.drive.api.storage.frappe.qb.from_", return_value=_FakeQuery())
	@patch("suite.drive.api.storage.frappe.session", new=SimpleNamespace(user="test@example.com"))
	def test_storage_breakdown_falls_back_to_default_team(
		self,
		_from,
		_get_list,
		_get_value,
		_get_teams,
		_get_default_team,
	):
		result = storage_breakdown(team=None, owned_only=True)

		self.assertEqual(result["limit"], 200 * MEGA_BYTE)
		self.assertEqual(result["entities"], [])
		self.assertEqual(result["total"], [])
		_get_default_team.assert_called_once()
