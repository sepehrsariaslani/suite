# Payam Yar Mail Branding Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rebrand the visible Mail product as پیام‌یار / Payam Yar, send Persian RTL account emails from مجموعه دهاتی, and safely make `admin@dehati.ir` an alias of the existing `info@dehati.ir` mailbox.

**Architecture:** Database-backed branding lives in the singleton Mail Settings DocType and is exposed through a small backend helper. Mail account messages use a dedicated safe HTML template and a formatted MIME sender derived from Frappe's active outgoing Email Account. Visible frontend strings use the existing locale catalog while technical identifiers and persisted `Home/Frappe Mail` paths remain unchanged.

**Tech Stack:** Frappe Framework 16, Python 3.14, Jinja email templates, Vue 3, frappe-ui, gettext PO catalogs, Vitest, Frappe integration tests, Stalwart JMAP management API.

## Global Constraints

- Mail-only branding: do not rename Suite, Drive, Calendar, routes, modules, DocTypes, APIs, or database keys.
- Persian display name is exactly `پیام‌یار`; English display name is exactly `Payam Yar`.
- Transactional sender display name defaults to exactly `مجموعه دهاتی`.
- Preserve the outgoing sender address chosen by Frappe's default outgoing Email Account.
- Preserve `Home/Frappe Mail` and protocol-level compatibility metadata.
- Invitation and OTP messages must be Persian, UTF-8, right-to-left, mobile-safe, and contain no remote scripts, fonts, or trackers.
- All code changes use test-first red-green-refactor cycles.
- Work and push only on `develop`.

---

### Task 1: Database-backed Mail branding

**Files:**
- Modify: `suite/mail/doctype/mail_settings/mail_settings.json`
- Modify: `suite/mail/doctype/mail_settings/mail_settings.py`
- Create: `suite/mail/branding.py`
- Create: `suite/mail/tests/test_branding.py`

**Interfaces:**
- Produces: `MailBranding(product_name_fa: str, product_name_en: str, sender_name: str)`.
- Produces: `get_mail_branding() -> MailBranding` using cached Mail Settings with safe defaults.
- Produces: `get_transactional_sender() -> str`, a MIME-formatted sender using the default outgoing Email Account address.

- [ ] **Step 1: Write failing tests for defaults, configured values, and formatted sender**

```python
class TestMailBranding(IntegrationTestCase):
    def test_empty_settings_use_payam_yar_defaults(self):
        with self.change_settings("Mail Settings", mail_product_name_fa="", mail_product_name_en="", mail_sender_name=""):
            self.assertEqual(get_mail_branding(), MailBranding("پیام‌یار", "Payam Yar", "مجموعه دهاتی"))

    @patch("suite.mail.branding.EmailAccount.find_default_outgoing")
    def test_sender_uses_configured_name_and_default_outgoing_address(self, find_default):
        find_default.return_value.email_id = "info@dehati.ir"
        with self.change_settings("Mail Settings", mail_sender_name="مجموعه دهاتی"):
            self.assertEqual(get_transactional_sender(), "مجموعه دهاتی <info@dehati.ir>")
```

- [ ] **Step 2: Run the tests and verify they fail because the branding module and fields do not exist**

Run: `docker exec den-v16-backend bench --site dehati.ir run-tests --app suite --module suite.mail.tests.test_branding`

Expected: FAIL importing `suite.mail.branding` or reading the new fields.

- [ ] **Step 3: Add the Branding section and fields to Mail Settings**

Add `branding_section`, `mail_product_name_fa`, `mail_product_name_en`, and `mail_sender_name` to `field_order`. Define defaults `پیام‌یار`, `Payam Yar`, and `مجموعه دهاتی`; use Data fields and Persian/English labels supported by the catalog. Add matching generated type declarations in `mail_settings.py`.

- [ ] **Step 4: Implement the focused branding helper**

```python
@dataclass(frozen=True)
class MailBranding:
    product_name_fa: str
    product_name_en: str
    sender_name: str

def get_mail_branding() -> MailBranding:
    settings = frappe.get_cached_doc("Mail Settings")
    return MailBranding(
        (settings.mail_product_name_fa or "پیام‌یار").strip(),
        (settings.mail_product_name_en or "Payam Yar").strip(),
        (settings.mail_sender_name or "مجموعه دهاتی").strip(),
    )

def get_transactional_sender() -> str:
    account = EmailAccount.find_default_outgoing()
    if not account or not account.email_id:
        return ""
    return formataddr((get_mail_branding().sender_name, account.email_id))
```

- [ ] **Step 5: Run the focused tests and schema validation**

Run: `docker exec den-v16-backend bench --site dehati.ir run-tests --app suite --module suite.mail.tests.test_branding`

Expected: PASS.

- [ ] **Step 6: Commit the branding configuration**

```bash
git add suite/mail/branding.py suite/mail/tests/test_branding.py suite/mail/doctype/mail_settings/mail_settings.json suite/mail/doctype/mail_settings/mail_settings.py
git commit -m "feat(mail): add configurable Payam Yar branding"
```

### Task 2: Persian RTL invitation and verification messages

**Files:**
- Create: `suite/templates/emails/payam_yar_account_email.html`
- Modify: `suite/mail/doctype/mail_account_request/mail_account_request.py`
- Modify: `suite/mail/tests/test_admin_members.py`

**Interfaces:**
- Consumes: `get_mail_branding()` and `get_transactional_sender()` from Task 1.
- Produces: invitation and OTP calls to `frappe.sendmail` with template `payam_yar_account_email`.

- [ ] **Step 1: Write failing unit-level sendmail assertions**

Patch `frappe.sendmail`, call `_send_invite_email()` and `_send_otp_email()`, and assert:

```python
sendmail.assert_called_once_with(
    recipients="recipient@example.test",
    sender="مجموعه دهاتی <info@dehati.ir>",
    subject="دعوت‌نامه عضویت در پیام‌یار",
    template="payam_yar_account_email",
    args=ANY,
    now=True,
)
self.assertEqual(kwargs["args"]["direction"], "rtl")
self.assertEqual(kwargs["args"]["button_label"], "تأیید و ساخت حساب")
self.assertIn("/mail/signup/", kwargs["args"]["action_url"])
```

For OTP, assert subject `کد تأیید پیام‌یار`, `verification_code`, and expiry minutes.

- [ ] **Step 2: Run focused tests and confirm the English generic-template behavior fails the assertions**

Run: `docker exec den-v16-backend bench --site dehati.ir run-tests --app suite --module suite.mail.tests.test_admin_members --test test_invitation_email_uses_payam_yar_branding`

Expected: FAIL showing the old English subject/template.

- [ ] **Step 3: Create the dedicated safe email template**

Implement a complete table-based HTML document with `<html lang="fa" dir="rtl">`, inline styles, escaped variables, a conditional CTA, a conditional LTR-isolated verification code, a visible fallback URL, and footer `این پیام از طرف مجموعه دهاتی و توسط پیام‌یار ارسال شده است.`.

- [ ] **Step 4: Update both send paths**

Use `get_mail_branding()` for the product/organization context and `get_transactional_sender()` for `sender`. Keep request key, OTP lifecycle, expiry, `now=True`, and audit logging unchanged.

- [ ] **Step 5: Run focused invitation, OTP, and existing account-flow tests**

Run: `docker exec den-v16-backend bench --site dehati.ir run-tests --app suite --module suite.mail.tests.test_admin_members`

Expected: PASS.

- [ ] **Step 6: Commit transactional email branding**

```bash
git add suite/templates/emails/payam_yar_account_email.html suite/mail/doctype/mail_account_request/mail_account_request.py suite/mail/tests/test_admin_members.py
git commit -m "feat(mail): send Persian Payam Yar account emails"
```

### Task 3: Visible Mail UI and PWA branding

**Files:**
- Modify: `frontend/src/apps/mail/components/LoginLayout.vue`
- Modify: `frontend/src/apps/mail/components/InstallPrompt.vue`
- Modify: `frontend/public/pwa/mail/manifest.webmanifest`
- Modify: `suite/templates/emails/base.html`
- Modify: `suite/templates/emails/_event_base.html`
- Modify: `suite/templates/emails/drive_invitation.html`
- Modify: `suite/templates/emails/drive_share.html`
- Modify: `suite/locale/fa.po`
- Create: `frontend/src/apps/mail/branding.test.ts`

**Interfaces:**
- Produces: Persian runtime translation `Frappe Mail -> پیام‌یار` and English static identity `Payam Yar`.
- Keeps internal folder and protocol strings unchanged.

- [ ] **Step 1: Add a failing scope test that scans user-visible Mail surfaces**

The Vitest test reads the manifest and scoped components/templates, expects `Payam Yar` in static English surfaces, and rejects visible `Frappe Mail`. Explicitly exclude `Home/Frappe Mail`, comments, tests, and JMAP protocol metadata.

- [ ] **Step 2: Run the scope test and verify it reports the existing visible names**

Run: `cd frontend && yarn test src/apps/mail/branding.test.ts`

Expected: FAIL listing LoginLayout, InstallPrompt, manifest, or Mail-owned email footers.

- [ ] **Step 3: Replace visible static names and complete Persian catalog entries**

Use `__('Frappe Mail')` where locale-aware runtime text is available with `msgstr "پیام‌یار"`. Use `Payam Yar` in the PWA manifest and static English email fallback surfaces. Do not touch persisted folder strings or technical headers.

- [ ] **Step 4: Run the scope test and catalog checks**

Run: `cd frontend && yarn test src/apps/mail/branding.test.ts`

Run: `python scripts/apply_persian_overrides.py --check`

Expected: both PASS with no duplicate or placeholder mismatch.

- [ ] **Step 5: Commit visible branding**

```bash
git add frontend/src/apps/mail frontend/public/pwa/mail/manifest.webmanifest suite/templates/emails suite/locale/fa.po
git commit -m "feat(mail): present Mail as Payam Yar"
```

### Task 4: Diagnose conflicts before mutating aliases

**Files:**
- Modify: `suite/mail/api/admin.py`
- Modify: `suite/mail/tests/test_admin_members.py`

**Interfaces:**
- Produces: `_find_address_owner(email: str) -> dict | None` for account primary addresses and aliases.
- Produces: a clear Persian-compatible validation error identifying whether an address is already a primary address or alias of another Stalwart resource.

- [ ] **Step 1: Add a failing integration test for an address owned by another account**

Create two test members and try adding the second member's primary address as an alias of the first. Assert that the exception mentions the conflicting address and owner instead of the generic mail-server error.

- [ ] **Step 2: Run the test and verify the current code fails with the generic Stalwart error**

Run: `docker exec den-v16-backend bench --site dehati.ir run-tests --app suite --module suite.mail.tests.test_admin_members --test test_add_alias_reports_existing_owner`

Expected: FAIL because `_add_alias` reaches Stalwart and returns `primaryKeyViolation`.

- [ ] **Step 3: Implement preflight ownership detection**

Before calling `set_aliases`, inspect account, group, and mailing-list primary addresses and enabled/disabled aliases using existing bulk service reads. If another object owns the address, throw a clear error containing the owner type and current primary address. Keep the same-resource duplicate behavior idempotent.

- [ ] **Step 4: Run alias and member integration tests**

Run: `docker exec den-v16-backend bench --site dehati.ir run-tests --app suite --module suite.mail.tests.test_admin_members`

Expected: PASS and no generic error for known ownership conflicts.

- [ ] **Step 5: Commit conflict diagnostics**

```bash
git add suite/mail/api/admin.py suite/mail/tests/test_admin_members.py
git commit -m "fix(mail): explain conflicting email address owners"
```

### Task 5: Safely free and attach `admin@dehati.ir`

**Files:**
- Operational state only: Stalwart account id `b`, Mail Settings, and alias set for account id `c`.

**Interfaces:**
- Consumes: Stalwart `AccountService.update`, Mail Settings `username`, cache clearing, and existing `add_member_email` logic.
- Produces: management identity `mail-system@dehati.ir`; `admin@dehati.ir` alias on the `info@dehati.ir` mailbox.

- [ ] **Step 1: Capture and verify current state**

Confirm Mail Settings username is `admin`, account `b` owns `admin@dehati.ir`, account `c` owns `info@dehati.ir`, and the management account has the Admin role. Abort if any id or ownership differs.

- [ ] **Step 2: Rename the management principal through its authenticated management session**

Update account `b` name to `mail-system`, then immediately update Mail Settings username to `mail-system`, clear `MANAGEMENT_SESSION_CACHE_KEY`, and verify a fresh management JMAP session can list domains and accounts. Keep the same encrypted password.

- [ ] **Step 3: Roll back if fresh management authentication fails**

Using the still-open authenticated connection, restore account `b` name to `admin`, restore Mail Settings username to `admin`, clear caches, and stop deployment. Do not proceed to alias creation.

- [ ] **Step 4: Add `admin@dehati.ir` to `info@dehati.ir` and verify routing**

Call the existing alias operation for member `info@dehati.ir`, reload member detail, and assert `admin@dehati.ir` appears as a non-primary enabled address. Send a test message to `admin@dehati.ir` and confirm it appears in the `info` inbox.

- [ ] **Step 5: Record the operational result without committing credentials**

Document only the management username and verification outcome in the deployment notes. Never write the Stalwart password or mailbox credentials to Git.

### Task 6: Full verification and deployment

**Files:**
- Modify if generated by translation tooling: `suite/locale/fa.po`
- No credential-bearing files.

**Interfaces:**
- Produces: migrated and deployed Payam Yar build on `dehati.ir` and a synced `develop` branch.

- [ ] **Step 1: Run backend regression tests**

Run: `docker exec den-v16-backend bench --site dehati.ir run-tests --app suite --module suite.mail.tests.test_branding`

Run: `docker exec den-v16-backend bench --site dehati.ir run-tests --app suite --module suite.mail.tests.test_admin_members`

Expected: PASS.

- [ ] **Step 2: Run the frontend suite and production build**

Run: `cd frontend && yarn test`

Run: `cd frontend && NODE_OPTIONS='--max-old-space-size=4096' yarn build`

Expected: all tests PASS and both application and service-worker builds complete.

- [ ] **Step 3: Run repository integrity checks**

Run: `git diff --check`

Run: `python scripts/apply_persian_overrides.py --check`

Expected: PASS with no whitespace errors, duplicate catalog entries, or placeholder mismatches.

- [ ] **Step 4: Migrate and deploy the site**

Run the normal containerized `bench --site dehati.ir migrate`, copy/build assets into the served location, clear website/cache state, and restart backend, workers, scheduler, websocket, and web-facing services without recreating the healthy Stalwart data volume.

- [ ] **Step 5: Perform live smoke tests**

Verify Mail login/signup/install surfaces show پیام‌یار in Persian. Send a new account invitation to a controlled external address; inspect Email Queue/MIME headers for `From: مجموعه دهاتی <info@dehati.ir>`, Persian subject/body, RTL markup, working action link, and successful delivery.

- [ ] **Step 6: Commit any final generated files and push**

```bash
git status --short
git push origin develop
```

Expected: local `develop` and `origin/develop` point to the same verified commit.
