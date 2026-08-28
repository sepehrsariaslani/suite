# Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from dataclasses import dataclass
from email.utils import formataddr

import frappe
from frappe.email.doctype.email_account.email_account import EmailAccount


@dataclass(frozen=True)
class MailBranding:
    product_name_fa: str
    product_name_en: str
    sender_name: str


def get_mail_branding() -> MailBranding:
    """Return administrator-configured Mail branding with safe defaults."""

    settings = frappe.get_cached_doc("Mail Settings")
    return MailBranding(
        product_name_fa=(settings.get("mail_product_name_fa") or "پیام‌یار").strip(),
        product_name_en=(settings.get("mail_product_name_en") or "Payam Yar").strip(),
        sender_name=(settings.get("mail_sender_name") or "مجموعه دهاتی").strip(),
    )


def get_transactional_sender() -> str:
    """Format the configured display name with Frappe's outgoing address."""

    account = EmailAccount.find_default_outgoing()
    if not account or not account.email_id:
        return ""

    return formataddr((get_mail_branding().sender_name, account.email_id))
