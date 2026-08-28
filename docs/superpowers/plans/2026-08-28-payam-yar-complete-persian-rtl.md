# Payam Yar Complete Persian and RTL Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Deliver a fully Persian, RTL Payam Yar user and administration experience while preserving content-aware direction for email bodies and technical values.

**Architecture:** Keep Suite's gettext catalogue as the translation source, extend the existing audit to find UI strings that bypass gettext, and apply RTL through shared root semantics plus narrow bidi-isolation utilities. Define native Frappe Email links once and reuse them in Payam Yar administration and a Suite-owned Desk workspace without modifying Frappe core.

**Tech Stack:** Frappe v16, Python 3.14, Vue 3, TypeScript, Vite 8, Vitest, gettext PO catalogues, Tailwind/frappe-ui, Frappe Workspace JSON.

## Global Constraints

- All Payam Yar product chrome, onboarding, forms, dialogs, states, and administration workflows require Persian translations.
- Received email bodies and compose content remain content-aware rather than forcibly RTL.
- Email addresses, URLs, code, DNS, SPF, DKIM, DMARC, tokens, and server values remain LTR with bidi isolation.
- Do not modify Frappe core.
- Native Frappe Email DocTypes remain Desk routes rather than being reimplemented in Suite.
- Keep changes on `develop` and use deterministic generated translation overrides.

---

### Task 1: Expand the Persian UI Audit

**Files:**
- Modify: `scripts/audit_persian_mail.py`
- Create: `scripts/test_audit_persian_mail.py`
- Modify: `scripts/apply_persian_overrides.py`

**Interfaces:**
- Produces: `untranslated_ui_candidates(paths: Iterable[Path]) -> list[UICandidate]`
- Produces: CLI output containing `direct_ui_candidates=<count>` and a non-zero exit when candidates remain.
- Consumes: existing `mail_runtime_keys()`, `read_catalogue()`, and placeholder validation.

- [ ] **Step 1: Write failing audit tests**

Add `unittest` cases proving that Vue text nodes and literal `label`, `title`, `placeholder`, `description`, `message`, tooltip, and aria values are reported, while comments, tests, protocol identifiers, and strings already wrapped in `__()` are ignored.

```python
def test_reports_direct_vue_text_and_literal_label(self):
    source = '<Button label="Add Member">Welcome</Button>'
    self.assertEqual(
        [candidate.text for candidate in candidates_from_source(Path("Member.vue"), source)],
        ["Add Member", "Welcome"],
    )

def test_ignores_translated_and_technical_values(self):
    source = '<Button :label="__(\'Add Member\')" /><code>DKIM</code>'
    self.assertEqual(candidates_from_source(Path("Member.vue"), source), [])
```

- [ ] **Step 2: Run the audit tests and confirm RED**

Run: `python3 -m unittest scripts.test_audit_persian_mail -v`

Expected: import or assertion failure because candidate scanning does not exist.

- [ ] **Step 3: Implement candidate scanning**

Add a small immutable candidate type and scanners for Vue templates and script object properties. Restrict scanning to `frontend/src/apps/mail` and shared onboarding files under `frontend/src/shell`; exclude tests, comments, technical elements, and explicit audit suppression comments.

```python
@dataclass(frozen=True)
class UICandidate:
    path: Path
    line: int
    text: str

def untranslated_ui_candidates(paths: Iterable[Path]) -> list[UICandidate]:
    return sorted(
        (candidate for path in paths for candidate in candidates_from_source(path, path.read_text())),
        key=lambda item: (str(item.path), item.line, item.text.casefold()),
    )
```

- [ ] **Step 4: Run focused tests and the real audit**

Run: `python3 -m unittest scripts.test_audit_persian_mail -v`

Expected: all scanner tests pass.

Run: `python3 scripts/audit_persian_mail.py --show`

Expected: non-zero with a concrete initial candidate list used by Task 2.

- [ ] **Step 5: Commit the audit**

```bash
git add scripts/audit_persian_mail.py scripts/test_audit_persian_mail.py
git commit -m "test(i18n): audit direct Payam Yar UI text"
```

---

### Task 2: Complete Persian Text Coverage

**Files:**
- Modify: candidate files reported under `frontend/src/apps/mail/**`
- Modify: `frontend/src/shell/SetupView.vue`
- Modify: `frontend/src/shell/InviteStep.vue`
- Modify: `frontend/src/shell/WorkspaceBrandingForm.vue`
- Modify: other `frontend/src/shell/**` files reported by the audit
- Modify: `scripts/persian_mail_overrides.py`
- Modify: `scripts/persian_core_ux_overrides.py`
- Modify: `suite/locale/fa.po` through the deterministic override script
- Modify: `suite/mail/api/**` only for Suite-owned user-facing server strings reported by review

**Interfaces:**
- Consumes: Task 1 direct-string audit.
- Produces: zero direct UI candidates and complete Persian catalogue entries with matching placeholders.

- [ ] **Step 1: Capture failing coverage evidence**

Run both audits before edits:

```bash
python3 scripts/audit_persian_mail.py --show
python3 scripts/apply_persian_overrides.py --check
```

Expected: direct UI candidate failures and/or missing new override entries.

- [ ] **Step 2: Route every visible literal through gettext**

Replace direct values with translated bindings and preserve semantic placeholders.

```vue
<FormControl
  :label="__('Primary Email')"
  :placeholder="__('name@example.com')"
  :description="__('Invitation and recovery messages are sent to this address.')"
/>
```

Dynamic messages must translate complete sentences instead of concatenating translated fragments.

```ts
const summary = count === 1 ? __('1 invitation will be sent') : __('{0} invitations will be sent', [count])
```

- [ ] **Step 3: Add reviewed Persian overrides**

Add natural Persian translations for every new key. Keep protocol terms such as DKIM, DMARC, TLS, OAuth, SPF, URL, API, IMAP, SMTP, and JMAP unchanged inside otherwise Persian sentences.

```python
PERSIAN_MAIL_OVERRIDES.update({
    "Admin Dashboard": "داشبورد مدیریت",
    "Email Accounts": "حساب‌های ایمیل",
    "Unhandled Email": "ایمیل‌های پردازش‌نشده",
})
```

- [ ] **Step 4: Regenerate the catalogue and verify GREEN**

Run:

```bash
python3 scripts/apply_persian_overrides.py
python3 scripts/apply_persian_overrides.py --check
python3 scripts/audit_persian_mail.py --show
```

Expected: `missing_or_empty=0`, `duplicates=0`, `placeholder_mismatches=0`, and `direct_ui_candidates=0`.

- [ ] **Step 5: Commit Persian coverage**

```bash
git add frontend/src/apps/mail frontend/src/shell scripts suite/locale/fa.po suite/mail/api
git commit -m "feat(i18n): complete Persian Payam Yar workflows"
```

---

### Task 3: Enforce Targeted RTL Semantics

**Files:**
- Create: `frontend/src/apps/mail/utils/direction.ts`
- Create: `frontend/src/apps/mail/utils/direction.test.ts`
- Modify: `frontend/src/index.css`
- Modify: `frontend/src/apps/mail/pages/MailLayout.vue`
- Modify: `frontend/src/apps/mail/components/EmailContent.vue`
- Modify: `frontend/src/apps/mail/components/ComposeMailEditor.vue`
- Modify: `frontend/src/shell/SetupView.vue`
- Modify: directional Mail components reported by source review

**Interfaces:**
- Produces: `contentDirection(value: string): 'rtl' | 'ltr' | 'auto'`
- Produces CSS contracts `.dir-ltr`, `.dir-auto`, `.mail-message-content`, and `.mail-compose-content`.
- Consumes: root `document.documentElement.dir` populated by `initializeTranslations()`.

- [ ] **Step 1: Write failing direction tests**

```ts
expect(contentDirection('سلام، این یک پیام است')).toBe('rtl')
expect(contentDirection('Hello, this is a message')).toBe('ltr')
expect(contentDirection('12345')).toBe('auto')
```

Add source assertions that message and compose containers use automatic/content-aware direction and technical controls use `.dir-ltr`.

- [ ] **Step 2: Run focused tests and confirm RED**

Run: `yarn vitest run src/apps/mail/utils/direction.test.ts`

Expected: module-not-found or failed direction assertions.

- [ ] **Step 3: Implement direction isolation**

```ts
const RTL = /[\u0590-\u08ff]/
const LTR = /[A-Za-z]/

export function contentDirection(value: string): 'rtl' | 'ltr' | 'auto' {
  const rtl = value.search(RTL)
  const ltr = value.search(LTR)
  if (rtl < 0 && ltr < 0) return 'auto'
  if (rtl < 0) return 'ltr'
  if (ltr < 0) return 'rtl'
  return rtl < ltr ? 'rtl' : 'ltr'
}
```

Use logical spacing/border properties and mirror only navigation controls whose semantics require it. Do not mirror attachment, status, brand, or protocol icons.

- [ ] **Step 4: Verify RTL tests and translation bootstrap**

Run:

```bash
yarn vitest run src/apps/mail/utils/direction.test.ts src/boot/translation.test.ts
```

Expected: all tests pass and Persian sets `html[dir=rtl]`.

- [ ] **Step 5: Commit RTL behavior**

```bash
git add frontend/src/index.css frontend/src/apps/mail frontend/src/shell/SetupView.vue
git commit -m "feat(mail): apply content-safe Persian RTL"
```

---

### Task 4: Make Frappe Email Tools Reusable and Visible

**Files:**
- Modify: `frontend/src/apps/mail/frappeEmailTools.ts`
- Modify: `frontend/src/apps/mail/frappeEmailTools.test.ts`
- Modify: `frontend/src/apps/mail/components/AppSidebar.vue`
- Modify: `frontend/src/apps/mail/pages/dashboard/OverviewView.vue`
- Create or modify: a focused tools card component under `frontend/src/apps/mail/components/`

**Interfaces:**
- Produces: `frappeEmailTools(): readonly FrappeEmailTool[]` with `key`, translation key, route, and icon identifier.
- Consumes: current Suite-admin state from `userStore()`.

- [ ] **Step 1: Write failing metadata and visibility tests**

```ts
expect(FRAPPE_EMAIL_TOOLS.map(({ key, route }) => [key, route])).toEqual([
  ['accounts', '/desk/email-account'],
  ['communications', '/desk/communication'],
  ['queue', '/desk/email-queue'],
  ['templates', '/desk/email-template'],
  ['unhandled', '/desk/unhandled-email'],
])
```

Add source/component tests proving both the sidebar and overview consume the shared metadata rather than duplicating links.

- [ ] **Step 2: Run focused tests and confirm RED**

Run: `yarn vitest run src/apps/mail/frappeEmailTools.test.ts`

Expected: metadata shape and overview-consumer assertions fail.

- [ ] **Step 3: Implement shared translated tools**

```ts
export const FRAPPE_EMAIL_TOOLS = [
  { key: 'accounts', label: 'Email Accounts', route: '/desk/email-account', icon: 'user' },
  { key: 'communications', label: 'Communications', route: '/desk/communication', icon: 'mails' },
  { key: 'queue', label: 'Email Queue', route: '/desk/email-queue', icon: 'clock' },
  { key: 'templates', label: 'Email Templates', route: '/desk/email-template', icon: 'scroll-text' },
  { key: 'unhandled', label: 'Unhandled Email', route: '/desk/unhandled-email', icon: 'mailbox' },
] as const
```

Render them in a clearly labelled Persian administration section and overview card. Keep them absent from ordinary non-admin mailbox navigation.

- [ ] **Step 4: Verify focused UI tests**

Run: `yarn vitest run src/apps/mail/frappeEmailTools.test.ts`

Expected: all tests pass.

- [ ] **Step 5: Commit tool discoverability**

```bash
git add frontend/src/apps/mail/frappeEmailTools* frontend/src/apps/mail/components frontend/src/apps/mail/pages/dashboard/OverviewView.vue
git commit -m "feat(mail): expose native Frappe email tools"
```

---

### Task 5: Add a Native Desk Email Workspace

**Files:**
- Create: `suite/mail/workspace/payam_yar_email/payam_yar_email.json`
- Create: `suite/mail/tests/test_email_workspace.py`

**Interfaces:**
- Produces: standard public Workspace `Payam Yar Email` restricted to `System Manager` with five canonical DocType shortcuts and a URL shortcut to `/mail/dashboard`.
- Consumes: native DocTypes from Frappe and the existing Suite Mail dashboard route.

- [ ] **Step 1: Write a failing workspace contract test**

```python
def test_payam_yar_workspace_exposes_native_email_tools(self):
    import json
    from pathlib import Path
    import frappe

    fixture = Path(frappe.get_app_path("suite", "mail", "workspace", "payam_yar_email", "payam_yar_email.json"))
    workspace = json.loads(fixture.read_text(encoding="utf-8"))
    self.assertEqual(
        {shortcut["link_to"] for shortcut in workspace["shortcuts"] if shortcut["type"] == "DocType"},
        {"Email Account", "Communication", "Email Queue", "Email Template", "Unhandled Email"},
    )
```

- [ ] **Step 2: Run the workspace test and confirm RED**

Run: `bench --site dehati.ir run-tests --app suite --module suite.mail.tests.test_email_workspace`

Expected: fixture-not-found failure.

- [ ] **Step 3: Add the standard Workspace JSON**

Create a public workspace with Persian-visible title `پیام‌یار`, module `Mail`, role `System Manager`, five DocType shortcuts, and one URL shortcut for `/mail/dashboard`. Use English source labels that resolve through the Persian catalogue where Frappe translates standard document labels.

- [ ] **Step 4: Run workspace test and migrate in test context**

Run: `bench --site dehati.ir run-tests --app suite --module suite.mail.tests.test_email_workspace`

Expected: all tests pass.

- [ ] **Step 5: Commit Desk integration**

```bash
git add suite/mail/workspace suite/mail/tests/test_email_workspace.py
git commit -m "feat(mail): add Payam Yar Desk workspace"
```

---

### Task 6: Regression, Build, Deploy, and Live Verification

**Files:**
- Modify only files revealed by failing verification.
- Generated build output: `suite/public/frontend/**` and `suite/www/suite.html` (normally ignored except tracked shell output).

**Interfaces:**
- Consumes: Tasks 1-5.
- Produces: migrated, built, cached-cleared live deployment on `dehati.ir` and synchronized `origin/develop`.

- [ ] **Step 1: Run deterministic translation checks**

```bash
python3 -m unittest scripts.test_audit_persian_mail -v
python3 scripts/apply_persian_overrides.py --check
python3 scripts/audit_persian_mail.py --show
```

Expected: all tests pass and every audit count is zero except the total runtime key count.

- [ ] **Step 2: Run focused and full test suites**

```bash
docker exec den-v16-backend bench --site dehati.ir run-tests --app suite --module suite.mail.tests.test_email_workspace
docker exec den-v16-backend bench --site dehati.ir run-tests --app suite --module suite.mail.tests.test_branding
cd frontend && yarn test
```

Expected: all relevant backend tests pass; frontend reports no failures.

- [ ] **Step 3: Build production assets**

```bash
cd frontend
NODE_OPTIONS='--max-old-space-size=4096' yarn build
```

Expected: Vite transforms all modules, emits hashed assets and Mail service worker, and exits `0`.

- [ ] **Step 4: Migrate and activate**

```bash
docker exec den-v16-backend bench --site dehati.ir migrate
docker exec den-v16-backend bench --site dehati.ir clear-cache
docker restart den-v16-backend den-v16-scheduler den-v16-queue-short den-v16-queue-long den-v16-websocket
```

Expected: migration exits `0`; all listed containers return to `Up` state.

- [ ] **Step 5: Verify live assets and routes**

Check that `/mail`, `/mail/dashboard`, the onboarding route, and the five Desk URLs return successful responses or expected authenticated redirects. Confirm live HTML references the just-built hashes and the service worker URL returns `200`.

- [ ] **Step 6: Verify browser-visible behavior**

With an authenticated Persian administrator, verify:

- Onboarding and Payam Yar user flows are Persian.
- The Mail and administration chrome are RTL on desktop and mobile widths.
- English email content, addresses, and DNS/DKIM values remain readable and unmirrored.
- The five Frappe Email tools appear in administration and Desk and open canonical routes.

- [ ] **Step 7: Push and confirm synchronization**

```bash
git diff --check
git status --short --branch
git push origin develop
git fetch origin develop
test "$(git rev-parse HEAD)" = "$(git rev-parse origin/develop)"
```

Expected: clean worktree, successful push, and identical local/remote commit IDs.
