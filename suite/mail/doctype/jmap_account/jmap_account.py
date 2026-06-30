# Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from typing import TYPE_CHECKING

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import cint

from suite.mail.jmap import (
	get_core_service,
	get_mailbox_id_by_role,
	invalidate_jmap_identities_cache,
	invalidate_jmap_mailboxes_cache,
)
from suite.mail.storage import get_blob_store, get_data_store
from suite.mail.storage.data_store import Entity

if TYPE_CHECKING:
	from suite.mail.jmap.services.core import CoreService

from suite.mail.utils import log_error
from suite.mail.utils.user import (
	get_account_emails,
	get_account_scoped_permission_query,
	has_account_scoped_permission,
)


class JMAPAccount(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		account_id: DF.Data
		block_remote_images: DF.Check
		create_contacts_after_email_submit: DF.Check
		default_outgoing_email: DF.Data | None
		destroy_email_after_submit: DF.Check
		destroy_newsletter_after_submit: DF.Check
		enable_screening: DF.Check
		is_personal: DF.Check
		last_active_sieve_script_id: DF.Data | None
		on_mark_as_junk: DF.Literal["Junk Sender's Mail", "Ask to Block Sender"]
	# end: auto-generated types

	"""Per-account settings shared across every user that has JMAP access to the account.

	The document is named by the bare JMAP account ID. Cache-related fields and actions
	operate on the *session user's* local store for the account, since the cache is kept
	per (user, account).
	"""

	@property
	def _user(self) -> str:
		"""The user whose JMAP connection backs per-user operations on this shared account.

		Uses the creating user during insert (set via flags) and the session user otherwise,
		so cache lookups reflect the user currently viewing the document.
		"""

		return self.flags.get("user") or frappe.session.user

	@property
	def core_service(self) -> "CoreService" | None:
		"""Return the JMAP core service for the account, or None if there is an error."""

		if self.flags.in_delete or not self.name:
			return None

		try:
			return get_core_service(self._user, self.name)
		except Exception:
			frappe.msgprint(f"Error getting JMAP core service for account {self.name}")
			return None

	@property
	def has_cached_jmap_identities(self) -> int:
		"""Check if there are cached JMAP identities for the account."""

		service = self.core_service
		if not service:
			return 0

		return cint(bool(service.cache.get("identities")))

	@property
	def has_cached_jmap_mailboxes(self) -> int:
		"""Check if there are cached JMAP mailboxes for the account."""

		service = self.core_service
		if not service:
			return 0

		return cint(bool(service.cache.get("mailboxes")))

	@property
	def total_cached_blobs(self) -> int:
		"""Get the total number of cached blobs for the account."""

		return get_blob_store(self.name).count()

	@property
	def total_cached_mail_messages(self) -> int:
		"""Get the total number of cached mail messages for the account."""

		return get_data_store(self.name).count(Entity.EMAIL)

	@property
	def total_cached_contact_cards(self) -> int:
		"""Get the total number of cached contact cards for the account."""

		return get_data_store(self.name).count(Entity.CONTACT_CARD)

	def validate(self) -> None:
		self.validate_default_outgoing_email()

	def validate_default_outgoing_email(self) -> None:
		"""Keep the default outgoing email valid: fall back to the account's first identity
		when the chosen one isn't one of the account's identities."""

		if not self.default_outgoing_email or frappe.flags.in_migrate:
			return

		try:
			emails = get_account_emails(self._user, self.name)
		except Exception:
			return

		if emails and self.default_outgoing_email not in emails:
			self.default_outgoing_email = emails[0]

	def after_insert(self) -> None:
		create_archive_mailbox(self._user, self.name)

	def on_update(self) -> None:
		# Toggling screening changes the automation sieve's screening gate, so regenerate it. Skipped
		# during migrate (no JMAP round-trips) and only when the flag actually changed.
		if frappe.flags.in_migrate:
			return

		if self.has_value_changed("enable_screening"):
			from suite.mail.api.sieve import build_automation_sieve
			from suite.mail.utils.user import get_session_account

			# JMAP Account is named by the shared account_id; resolve it to the session user's
			# account handle for the sieve regeneration.
			build_automation_sieve(get_session_account(self.name))

	def after_delete(self) -> None:
		"""Clear all caches related to the account when the settings are deleted."""

		self.clear_cached_jmap_identities()
		self.clear_cached_jmap_mailboxes()
		self.clear_cached_mail_messages()
		self.clear_cached_contact_cards()
		self.clear_cached_blobs()

	@frappe.whitelist()
	def clear_cached_jmap_identities(self) -> None:
		"""Clear all cached JMAP identities for the current account."""

		if self.has_clear_cache_permission():
			invalidate_jmap_identities_cache(self.name)

	@frappe.whitelist()
	def clear_cached_jmap_mailboxes(self) -> None:
		"""Clear all cached JMAP mailboxes for the current account."""

		if self.has_clear_cache_permission():
			invalidate_jmap_mailboxes_cache(self.name)

	@frappe.whitelist()
	def clear_cached_blobs(self) -> None:
		"""Clear all cached JMAP blobs for the current account."""

		if not self.has_clear_cache_permission():
			return

		get_blob_store(self.name).delete_all()

	@frappe.whitelist()
	def clear_cached_mail_messages(self) -> None:
		"""Clear all cached mail messages for the current account."""

		if not self.has_clear_cache_permission():
			return

		get_data_store(self.name).delete_all(Entity.EMAIL)

	@frappe.whitelist()
	def clear_cached_contact_cards(self) -> None:
		"""Clear all cached contact cards for the current account."""

		if not self.has_clear_cache_permission():
			return

		get_data_store(self.name).delete_all(Entity.CONTACT_CARD)

	def has_clear_cache_permission(self) -> bool:
		"""Check if the session user has permission to clear cache."""

		if has_permission(self, "write"):
			return True

		frappe.throw(
			_("You do not have permission to clear the cache for this account."), frappe.PermissionError
		)

	def _db_set(
		self,
		update_modified: bool = True,
		commit: bool = False,
		notify: bool = False,
		**kwargs,
	) -> None:
		"""Updates the document with the given key-value pairs."""

		self.db_set(kwargs, update_modified=update_modified, notify=notify, commit=commit)


def get_or_create_account_settings(account: str, user: str | None = None) -> str:
	"""Return the name of the (shared) JMAP Account for the given bare `account`,
	creating it if it does not already exist. The document is named by the account ID."""

	if frappe.db.exists("JMAP Account", account):
		return account

	user = user or frappe.session.user

	settings = frappe.new_doc("JMAP Account")
	settings.account_id = account
	# Carry the user so after_insert / validate can reach JMAP for this account.
	settings.flags.user = user

	# Default the outgoing sender to the account's first identity.
	try:
		emails = get_account_emails(user, account)
		if emails:
			settings.default_outgoing_email = emails[0]
	except Exception:
		pass

	settings.flags.ignore_links = True
	settings.insert(ignore_permissions=True)

	return settings.name


def sync_account_settings(user: str, accounts: dict[str, dict]) -> None:
	"""Ensure a shared JMAP Account document exists for each of the user's accounts.

	Settings are shared by account ID across every user with access, so documents for
	accounts the user can no longer see are intentionally left untouched.
	"""

	for account in accounts.keys():
		get_or_create_account_settings(account, user=user)


def backfill_default_outgoing_emails() -> None:
	"""Resolve each account's default outgoing email against its identities.

	Run as a background job (e.g. after the Outgoing-settings migration), where JMAP is
	reachable — unlike during `bench migrate`. Keeps an existing default if it's one of
	the account's identities, otherwise uses the account's first identity.
	"""

	from suite.mail.jmap import get_jmap_connection

	for user in frappe.get_all("User Settings", filters={"username": ["is", "set"]}, pluck="user"):
		try:
			account_ids = list(get_jmap_connection(user, ignore_permissions=True).accounts.keys())
		except Exception:
			continue

		for account_id in account_ids:
			if not frappe.db.exists("JMAP Account", account_id):
				continue

			try:
				emails = get_account_emails(user, account_id)
			except Exception:
				continue

			if not emails:
				continue

			current = frappe.db.get_value("JMAP Account", account_id, "default_outgoing_email")
			resolved = current if current in emails else emails[0]
			if resolved != current:
				frappe.db.set_value(
					"JMAP Account",
					account_id,
					"default_outgoing_email",
					resolved,
					update_modified=False,
				)

	frappe.db.commit()


def get_permission_query_condition(user: str | None = None) -> str:
	# JMAP Account is named directly by the account ID, so scope on `name`.
	return get_account_scoped_permission_query("JMAP Account", column="name", user=user)


def has_permission(doc: Document, ptype: str, user: str | None = None) -> bool:
	if doc.doctype != "JMAP Account":
		return False

	return has_account_scoped_permission(doc, column="name", user=user)


def create_archive_mailbox(user: str, account: str) -> None:
	"""Create the archive mailbox for the account if it does not already exist."""

	try:
		get_mailbox_id_by_role(user, account, "archive", create_if_not_exists=True)

	except Exception:
		log_error(
			_("Archive Mailbox Creation Error"),
			_("Failed to create archive mailbox for account {0}").format(account),
		)
