import frappe
from frappe.translate import get_all_translations


@frappe.whitelist(allow_guest=True)
def get_translations() -> dict:
    language = _get_language()
    base_language = language.split("-")[0].split("_")[0]
    return {
        "language": language,
        "direction": "rtl" if base_language in {"ar", "fa", "he", "ur"} else "ltr",
        "messages": get_all_translations(language),
    }


def _get_language() -> str:
    if frappe.session.user != "Guest":
        language = frappe.db.get_value("User", frappe.session.user, "language")
        if language:
            return language

    return frappe.db.get_single_value("System Settings", "language") or "en"
