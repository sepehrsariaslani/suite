# Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt


from uuid import uuid7

import frappe
from frappe import _
from frappe.model.document import Document

from suite.mail.utils.user import is_system_manager


class UserAccount(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		account: DF.Link
		user: DF.Link
		user_settings: DF.Link
	# end: auto-generated types

	def autoname(self) -> None:
		self.name = str(uuid7())


def get_user_jmap_account_ids(user: str | None = None) -> list[str]:
	"""Returns the list of JMAP account IDs for the given user. If no user is provided, it defaults to the current session user."""

	user = user or frappe.session.user
	accounts = frappe.db.get_all("User Account", {"user": user}, pluck="account")

	return accounts


def is_jmap_account_belongs_to_user(
	account_id: str, user: str | None = None, raise_exception: bool = False
) -> bool:
	"""Checks if the given JMAP account ID belongs to the specified user. If no user is provided, it defaults to the current session user."""

	user = user or frappe.session.user
	exists = bool(frappe.db.exists("User Account", {"user": user, "account": account_id}))

	if raise_exception and not exists:
		frappe.throw(
			_("JMAP account {0} does not belong to the user {1}.").format(
				frappe.bold(account_id), frappe.bold(user)
			)
		)

	return exists


def has_permission(doc: "Document", ptype: str, user: str | None = None) -> bool:
	if doc.doctype != "User Account":
		return False

	user = user or frappe.session.user
	return doc.user == user or is_system_manager(user)


def get_permission_query_condition(user: str | None = None) -> str | None:
	user = user or frappe.session.user
	if is_system_manager(user):
		return ""

	return f"""`tabUser Account`.user = '{user}'"""
