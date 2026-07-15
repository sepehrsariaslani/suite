import frappe
from frappe.translate import get_all_translations


@frappe.whitelist(allow_guest=True)
def get_translations() -> dict:
	"""Return the current locale and its complete translation catalogue.

	The unified Suite SPA uses one catalogue for every embedded app. Loading it
	once during bootstrap prevents route-specific catalogues from racing and
	keeps the shell, error pages, and lazy-loaded apps consistently translated.
	"""
	language = _get_language()
	return {
		"language": language,
		"direction": "rtl" if language.split("-")[0].split("_")[0] in {"ar", "fa", "he", "ur"} else "ltr",
		"messages": get_all_translations(language),
	}


def _get_language() -> str:
	if frappe.session.user != "Guest":
		language = frappe.db.get_value("User", frappe.session.user, "language")
		if language:
			return language

	return frappe.db.get_single_value("System Settings", "language") or "en"
