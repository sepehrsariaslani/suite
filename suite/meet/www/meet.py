import frappe
from suite.meet.utils.sfu_config import get_sfu_config

no_cache = 1


def get_context():
	csrf_token = frappe.sessions.get_csrf_token()
	frappe.db.commit()
	context = frappe._dict()
	context.boot = get_boot()
	context.boot.csrf_token = csrf_token
	return context


@frappe.whitelist(methods=["POST"], allow_guest=True)
def get_context_for_dev():
	if not frappe.conf.developer_mode:
		frappe.throw("This method is only meant for developer mode")
	return get_boot()


def get_boot():
	sfu_config = get_sfu_config()
	return frappe._dict(
		frappe_version=frappe.__version__,
		site_name=frappe.local.site,
		is_system_user=frappe.session.data.user_type == "System User",
		sfu_enabled=bool(sfu_config.get("sfu_server_url") and sfu_config.get("sfu_secret")),
	)
