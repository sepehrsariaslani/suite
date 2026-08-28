import json
from pathlib import Path

from frappe.tests import IntegrationTestCase


WORKSPACE_PATH = (
    Path(__file__).resolve().parents[1]
    / "workspace"
    / "payam_yar_email"
    / "payam_yar_email.json"
)


class TestPayamYarEmailWorkspace(IntegrationTestCase):
    def test_workspace_exposes_payam_yar_and_native_email_tools(self):
        workspace = json.loads(WORKSPACE_PATH.read_text(encoding="utf-8"))

        self.assertEqual(workspace["label"], "پیام‌یار")
        self.assertEqual(workspace["module"], "Mail")
        self.assertEqual(workspace["public"], 1)
        self.assertEqual(workspace["roles"], [{"role": "System Manager"}])

        shortcuts = {
            shortcut["label"]: shortcut
            for shortcut in workspace["shortcuts"]
        }
        self.assertEqual(shortcuts["داشبورد پیام‌یار"]["url"], "/mail/dashboard")
        self.assertEqual(
            {
                label: shortcut["link_to"]
                for label, shortcut in shortcuts.items()
                if shortcut["type"] == "DocType"
            },
            {
                "حساب‌های ایمیل": "Email Account",
                "ارتباطات": "Communication",
                "صف ایمیل": "Email Queue",
                "الگوهای ایمیل": "Email Template",
                "ایمیل‌های پردازش‌نشده": "Unhandled Email",
            },
        )

