import frappe

from suite.mail.jmap import parse_account


def execute() -> None:
	"""Backfill `Mail Queue.account` from the old "user:account" handle.

	The `account` handle was replaced by a bare `account` (the `user` field still carries
	the credentials used to send the message). Each row keeps its user, so we just split the
	stored handle to fill account in.
	"""

	if not frappe.db.has_column("Mail Queue", "account"):
		# Fresh install (or already migrated) — nothing to backfill.
		return

	MQ = frappe.qb.DocType("Mail Queue")

	# Map each distinct handle to its account and update in bulk (Mail Queue can be large).
	handles = frappe.qb.from_(MQ).select(MQ.account).distinct().where(MQ.account.isnotnull()).run(pluck=True)

	for handle in handles:
		try:
			account = parse_account(handle)[1]
		except Exception:
			continue  # skip malformed handles rather than abort the migration

		(frappe.qb.update(MQ).set(MQ.account, account).where(MQ.account == handle)).run()
