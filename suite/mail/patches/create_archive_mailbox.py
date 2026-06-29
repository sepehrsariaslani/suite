import frappe

from suite.mail.doctype.jmap_account.jmap_account import create_archive_mailbox


def execute() -> None:
	# JMAP Account was later reshaped to be shared per account ID, dropping the
	# `account` (`user:account_id`) column. Without it we can't build the per-user JMAP
	# connection this patch needs, so it only runs against the legacy schema; the archive
	# mailbox is created on demand by JMAP Account.after_insert thereafter.
	if not frappe.db.has_column("JMAP Account", "account"):
		return

	for account in frappe.get_all("JMAP Account", pluck="account"):
		create_archive_mailbox(account)
