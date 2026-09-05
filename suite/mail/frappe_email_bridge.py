"""Mirror sent Frappe Email Queue messages into the matching Suite JMAP Sent mailbox."""

from __future__ import annotations

from email import policy
from email.parser import BytesParser
from typing import Any

import frappe
from frappe.utils import cint, now_datetime

from suite.mail.jmap import get_email_service, get_mailbox_service

MAX_SYNC_BATCH = 100


def _get_or_create_mirror(queue_name: str):
    if name := frappe.db.get_value("Suite Frappe Email Mirror", {"email_queue": queue_name}, "name"):
        return frappe.get_doc("Suite Frappe Email Mirror", name)

    try:
        return frappe.get_doc(
            {"doctype": "Suite Frappe Email Mirror", "email_queue": queue_name, "status": "Pending"}
        ).insert(ignore_permissions=True)
    except frappe.DuplicateEntryError:
        name = frappe.db.get_value("Suite Frappe Email Mirror", {"email_queue": queue_name}, "name")
        return frappe.get_doc("Suite Frappe Email Mirror", name)


def _resolve_jmap_account(queue) -> str:
    if not queue.email_account:
        frappe.throw("The email queue does not identify an Email Account.")

    account = frappe.get_doc("Email Account", queue.email_account)
    email = str(account.email_id or "").strip().lower()
    if not email:
        frappe.throw("The Email Account has no sender address.")

    jmap_account = frappe.db.get_value("User Account", {"user": email}, "account")
    if not jmap_account:
        frappe.throw(f"No Suite JMAP account is linked to {email}.")
    return jmap_account


def _queue_message(queue) -> bytes:
    raw_message = str(queue.message or "")
    if not raw_message:
        frappe.throw("The email queue no longer contains its MIME message.")

    recipients = [str(row.recipient).strip() for row in queue.recipients if str(row.recipient or "").strip()]
    to_header = ", ".join(recipients) if recipients else "Undisclosed recipients"
    raw_message = raw_message.replace("<!--recipient-->", to_header)
    message = BytesParser(policy=policy.SMTP).parsebytes(raw_message.encode("utf-8"))
    if "X-Frappe-Email-Queue" in message:
        message.replace_header("X-Frappe-Email-Queue", queue.name)
    else:
        message["X-Frappe-Email-Queue"] = queue.name
    return message.as_bytes(policy=policy.SMTP)


def _import_queue_into_sent(queue, jmap_account: str) -> str:
    email_service = get_email_service(jmap_account, ignore_permissions=True)
    sent_mailbox_id = get_mailbox_service(jmap_account, ignore_permissions=True).get_mailbox_id_by_role(
        "sent", create_if_not_exists=True, raise_exception=True
    )
    blob = email_service.upload_blob(_queue_message(queue), content_type="message/rfc822")
    creation_id = f"frappe-{queue.name}"
    response = email_service._call(
        email_service.capabilities,
        method_calls=[
            [
                "Email/import",
                {
                    "accountId": jmap_account,
                    "emails": {
                        creation_id: {
                            "blobId": blob["blobId"],
                            "mailboxIds": {sent_mailbox_id: True},
                            "keywords": {"$seen": True},
                        }
                    },
                },
                creation_id,
            ]
        ],
    )
    result = (response.get("methodResponses") or [[None, {}, None]])[0][1]
    imported = (result.get("created") or {}).get(creation_id)
    if not imported:
        frappe.throw(f"Suite could not import the sent message: {(result.get('notCreated') or {}).get(creation_id) or 'unknown error'}")
    return imported["id"]


def _mark_synced(mirror, jmap_account: str, jmap_email_id: str) -> None:
    mirror.db_set(
        {
            "jmap_account": jmap_account,
            "jmap_email_id": jmap_email_id,
            "status": "Synced",
            "last_attempt_on": now_datetime(),
            "error": None,
        },
        update_modified=True,
    )


def _mark_failed(mirror, error: Exception) -> None:
    mirror.db_set(
        {
            "status": "Failed",
            "attempts": cint(mirror.attempts) + 1,
            "last_attempt_on": now_datetime(),
            "error": frappe.get_traceback(with_context=False)[-4000:],
        },
        update_modified=True,
    )


def sync_sent_email_queue(queue_name: str) -> dict[str, Any]:
    """Import one successfully sent Frappe message into its Suite Sent mailbox."""

    queue = frappe.get_doc("Email Queue", queue_name)
    if queue.status != "Sent":
        return {"queue_name": queue.name, "state": "skipped_not_sent"}

    mirror = _get_or_create_mirror(queue.name)
    if mirror.status == "Synced" and mirror.jmap_email_id:
        return {"queue_name": queue.name, "state": "already_synced", "jmap_email_id": mirror.jmap_email_id}

    try:
        jmap_account = _resolve_jmap_account(queue)
        jmap_email_id = _import_queue_into_sent(queue, jmap_account)
        _mark_synced(mirror, jmap_account, jmap_email_id)
        return {"queue_name": queue.name, "state": "synced", "jmap_email_id": jmap_email_id}
    except Exception as error:
        _mark_failed(mirror, error)
        return {"queue_name": queue.name, "state": "failed"}


def sync_pending_frappe_sent_emails(limit: int = MAX_SYNC_BATCH) -> dict[str, int]:
    """Scheduled bounded backfill for sent messages that do not have a Suite mirror."""

    limit = max(1, min(cint(limit), MAX_SYNC_BATCH))
    queues = frappe.get_all(
        "Email Queue",
        filters={"status": "Sent", "email_account": ["is", "set"]},
        fields=["name"],
        order_by="creation asc",
        limit_page_length=limit,
    )
    outcomes = {"synced": 0, "already_synced": 0, "failed": 0, "skipped_not_sent": 0}
    for row in queues:
        result = sync_sent_email_queue(row.name)
        outcomes[result["state"]] = outcomes.get(result["state"], 0) + 1
    return outcomes
