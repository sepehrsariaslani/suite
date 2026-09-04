"""Bounded central outbound-email service for MCP consumers."""

from __future__ import annotations

import hashlib
import json
import re
from typing import Any

import frappe

MAX_RECIPIENTS = 20
MAX_ATTACHMENTS = 20
MAX_ATTACHMENT_BYTES = 15 * 1024 * 1024
MAX_SUBJECT = 240
MAX_BODY = 12000
EMAIL_RE = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")
IDEMPOTENCY_RE = re.compile(r"^[A-Za-z0-9._:-]{16,160}$")
NAME_RE = re.compile(r"^[A-Za-z0-9 _./:@+-]{1,180}$")


def _require_system_manager() -> None:
    if "System Manager" not in frappe.get_roles(frappe.session.user):
        frappe.throw("System Manager permission is required.", frappe.PermissionError)


def _email(value: Any, label: str) -> str:
    address = str(value or "").strip().lower()
    if not EMAIL_RE.fullmatch(address):
        frappe.throw(f"Invalid {label} email address.", frappe.ValidationError)
    return address


def _emails(value: Any, label: str, *, required: bool = False) -> list[str]:
    if value in (None, "", []):
        if required:
            frappe.throw(f"{label} is required.", frappe.ValidationError)
        return []
    if not isinstance(value, (list, tuple)) or len(value) > MAX_RECIPIENTS:
        frappe.throw(f"{label} must contain at most {MAX_RECIPIENTS} addresses.", frappe.ValidationError)
    return list(dict.fromkeys(_email(row, label) for row in value))


def _text(value: Any, label: str, maximum: int, *, required: bool = True) -> str:
    text = str(value or "").strip()
    if (required and not text) or len(text) > maximum:
        frappe.throw(f"{label} is invalid.", frappe.ValidationError)
    return text


def _safe_name(value: Any, label: str) -> str:
    name = str(value or "").strip()
    if not NAME_RE.fullmatch(name):
        frappe.throw(f"Invalid {label}.", frappe.ValidationError)
    return name


def _account_summary(row: Any) -> dict[str, Any]:
    return {
        "name": row.name,
        "email": row.email_id,
        "display_name": row.email_account_name or row.name,
        "outgoing": bool(row.enable_outgoing),
        "incoming": bool(row.enable_incoming),
        "default_outgoing": bool(row.default_outgoing),
        "default_incoming": bool(row.default_incoming),
        "service": row.service or "SMTP",
    }


def _outgoing_account(sender: Any, email_account: Any):
    clean_sender = _email(sender, "sender")
    account_name = _safe_name(email_account, "Email Account")
    account = frappe.get_doc("Email Account", account_name)
    if not account.enable_outgoing or str(account.email_id or "").lower() != clean_sender:
        frappe.throw("Selected sender is not an active outgoing Email Account.", frappe.PermissionError)
    return clean_sender, account


def _attachments(value: Any) -> tuple[list[dict[str, str]], list[dict[str, Any]]]:
    if value in (None, "", []):
        return [], []
    if not isinstance(value, (list, tuple)) or len(value) > MAX_ATTACHMENTS:
        frappe.throw(f"attachments must contain at most {MAX_ATTACHMENTS} File names.", frappe.ValidationError)
    names = list(dict.fromkeys(_safe_name(row, "File") for row in value))
    total = 0
    queue_rows: list[dict[str, str]] = []
    preview_rows: list[dict[str, Any]] = []
    for name in names:
        file_doc = frappe.get_doc("File", name)
        file_doc.check_permission("read")
        size = int(file_doc.file_size or 0)
        total += size
        if total > MAX_ATTACHMENT_BYTES:
            frappe.throw("Email attachment payload exceeds the allowed size.", frappe.ValidationError)
        queue_rows.append({"fid": file_doc.name})
        preview_rows.append({"name": file_doc.name, "file_name": file_doc.file_name, "file_size": size})
    return queue_rows, preview_rows


def _reference(doctype: Any, name: Any) -> tuple[str | None, str | None]:
    if doctype in (None, "") and name in (None, ""):
        return None, None
    if not doctype or not name:
        frappe.throw("reference_doctype and reference_name must be supplied together.", frappe.ValidationError)
    clean_doctype = _safe_name(doctype, "reference DocType")
    clean_name = _safe_name(name, "reference name")
    doc = frappe.get_doc(clean_doctype, clean_name)
    doc.check_permission("read")
    return clean_doctype, clean_name


def _fingerprint(payload: dict[str, Any]) -> str:
    encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


def _template_context(value: Any) -> dict[str, Any]:
    if value in (None, "", {}):
        return {}
    if not isinstance(value, dict):
        frappe.throw("template_context must be an object.", frappe.ValidationError)
    encoded = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    if len(encoded) > 12000:
        frappe.throw("template_context is too large.", frappe.ValidationError)
    return json.loads(encoded)


@frappe.whitelist()
def list_email_accounts() -> dict[str, Any]:
    _require_system_manager()
    rows = frappe.get_all(
        "Email Account",
        fields=["name", "email_id", "email_account_name", "enable_outgoing", "enable_incoming", "default_outgoing", "default_incoming", "service"],
        order_by="default_outgoing desc, email_id asc",
        limit_page_length=100,
    )
    return {"accounts": [_account_summary(row) for row in rows], "bounded": True}


@frappe.whitelist()
def get_default_outgoing_email() -> dict[str, Any]:
    _require_system_manager()
    rows = frappe.get_all("Email Account", filters={"enable_outgoing": 1, "default_outgoing": 1}, fields=["name", "email_id", "email_account_name", "enable_outgoing", "enable_incoming", "default_outgoing", "default_incoming", "service"], limit_page_length=1)
    return {"account": _account_summary(rows[0]) if rows else None}


@frappe.whitelist()
def list_email_templates() -> dict[str, Any]:
    _require_system_manager()
    rows = frappe.get_all("Email Template", fields=["name", "subject", "use_html"], order_by="name asc", limit_page_length=100)
    return {"templates": [{"name": row.name, "subject": row.subject, "use_html": bool(row.use_html)} for row in rows], "bounded": True}


@frappe.whitelist()
def render_email_template(name: str, context: dict[str, Any] | None = None, sender: str | None = None) -> dict[str, Any]:
    _require_system_manager()
    template = frappe.get_doc("Email Template", _safe_name(name, "Email Template"))
    template.check_permission("read")
    values = _template_context(context)
    clean_sender = _email(sender, "sender") if sender else None
    rendered = template.get_formatted_email(values, sender=clean_sender)
    return {"template": template.name, "subject": _text(rendered["subject"], "template subject", MAX_SUBJECT), "message": _text(rendered["message"], "template message", MAX_BODY)}


@frappe.whitelist()
def prepare_email(sender: str, email_account: str, recipients: list[str], subject: str | None = None, message: str | None = None, cc: list[str] | None = None, bcc: list[str] | None = None, reply_to: str | None = None, attachment_file_names: list[str] | None = None, reference_doctype: str | None = None, reference_name: str | None = None, template_name: str | None = None, template_context: dict[str, Any] | None = None) -> dict[str, Any]:
    _require_system_manager()
    clean_sender, account = _outgoing_account(sender, email_account)
    if template_name:
        rendered = render_email_template(template_name, template_context, clean_sender)
        subject = subject or rendered["subject"]
        message = message or rendered["message"]
    queue_attachments, preview_attachments = _attachments(attachment_file_names)
    reference = _reference(reference_doctype, reference_name)
    preview = {
        "sender": clean_sender,
        "email_account": account.name,
        "recipients": _emails(recipients, "recipients", required=True),
        "cc": _emails(cc, "cc"),
        "bcc": _emails(bcc, "bcc"),
        "reply_to": _email(reply_to, "reply_to") if reply_to else None,
        "subject": _text(subject, "subject", MAX_SUBJECT),
        "message": _text(message, "message", MAX_BODY),
        "attachments": preview_attachments,
        "reference_doctype": reference[0],
        "reference_name": reference[1],
        "template_name": _safe_name(template_name, "Email Template") if template_name else None,
        "template_context": _template_context(template_context),
    }
    preview["attachment_queue_rows"] = queue_attachments
    fingerprint = _fingerprint(preview)
    preview.pop("attachment_queue_rows")
    return {"state": "awaiting_confirmation", "preview": preview, "confirmation": {"required": True, "preview_fingerprint": fingerprint, "prompt_fa": "فرستنده، گیرندگان، عنوان، متن و پیوست‌ها را تایید می‌کنید؟"}}


@frappe.whitelist()
def send_email(sender: str, email_account: str, recipients: list[str], subject: str | None = None, message: str | None = None, cc: list[str] | None = None, bcc: list[str] | None = None, reply_to: str | None = None, attachment_file_names: list[str] | None = None, reference_doctype: str | None = None, reference_name: str | None = None, template_name: str | None = None, template_context: dict[str, Any] | None = None, confirmed: bool = False, preview_fingerprint: str | None = None, idempotency_key: str | None = None) -> dict[str, Any]:
    previewed = prepare_email(sender, email_account, recipients, subject, message, cc, bcc, reply_to, attachment_file_names, reference_doctype, reference_name, template_name, template_context)
    fingerprint = previewed["confirmation"]["preview_fingerprint"]
    if preview_fingerprint != fingerprint:
        frappe.throw("Email preview changed; prepare and confirm again.", frappe.ValidationError)
    if confirmed is not True:
        return {**previewed, "state": "confirmation_required"}
    key = str(idempotency_key or "")
    if not IDEMPOTENCY_RE.fullmatch(key):
        frappe.throw("Invalid idempotency key.", frappe.ValidationError)
    request_hash = _fingerprint({"fingerprint": fingerprint, "key": key, "owner": frappe.session.user})
    existing = frappe.get_all("Suite MCP Email Request", filters={"owner": frappe.session.user, "idempotency_key": key}, fields=["name", "request_hash", "status", "queue_name"], limit_page_length=1)
    if existing:
        row = existing[0]
        if row.request_hash != request_hash:
            frappe.throw("Idempotency key was already used for another email.", frappe.ValidationError)
        return {"state": "email_sent", "idempotent_replay": True, "queue_names": [row.queue_name] if row.queue_name else []}
    preview = previewed["preview"]
    queue_attachments, _ = _attachments(attachment_file_names)
    request = frappe.get_doc({"doctype": "Suite MCP Email Request", "idempotency_key": key, "request_hash": request_hash, "preview_fingerprint": fingerprint, "status": "Prepared"}).insert(ignore_permissions=True)
    queue = frappe.sendmail(recipients=preview["recipients"], sender=preview["sender"], subject=preview["subject"], message=preview["message"], cc=preview["cc"], bcc=preview["bcc"], reply_to=preview["reply_to"], attachments=queue_attachments, reference_doctype=preview["reference_doctype"], reference_name=preview["reference_name"])
    request.status = "Sent"
    request.queue_name = getattr(queue, "name", None)
    request.save(ignore_permissions=True)
    return {"state": "email_sent", "idempotent_replay": False, "queue_names": [request.queue_name] if request.queue_name else []}


@frappe.whitelist()
def get_email_delivery_status(queue_name: str) -> dict[str, Any]:
    _require_system_manager()
    queue = frappe.get_doc("Email Queue", _safe_name(queue_name, "Email Queue"))
    error = str(queue.error or "")
    category = "none"
    if error:
        category = "authentication" if "auth" in error.lower() else "recipient" if "recipient" in error.lower() else "delivery_failed"
    return {"queue": {"name": queue.name, "status": queue.status, "retry": int(queue.retry or 0), "sender": queue.sender, "email_account": queue.email_account, "creation": str(queue.creation), "modified": str(queue.modified), "failure_category": category}}
