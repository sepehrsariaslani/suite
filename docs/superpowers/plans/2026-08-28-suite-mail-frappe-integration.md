# Suite Mail And Frappe Email Integration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Repair Suite Mail, complete its Persian interface, and make the existing `info@dehati.ir` Stalwart mailbox available to Administrator and Frappe transactional email without duplicating Frappe's mail subsystems.

**Architecture:** Stalwart remains authoritative. Suite uses JMAP for the interactive mailbox, while one standard Frappe Email Account uses dedicated Stalwart app credentials for ERP transport. Frontend compatibility and localization changes are committed to `develop`; secrets and live site configuration remain outside Git.

**Tech Stack:** Vue 3, Vite 8, Vitest 4, frappe-ui Tabs, Frappe v16, Suite Mail, JMAP, Stalwart v0.16.16, SMTP/IMAP, gettext PO.

**Execution:** Run inline on the existing `develop` checkout because this checkout is the deployed source tree and the user explicitly selected `develop`. Use small verified commits and do not modify `main`.

## Global Constraints

- Keep `dehati.ir` and ERP APIs available throughout deployment.
- Keep Stalwart as the authoritative server for `info@dehati.ir`.
- Never print, commit, or pass a password in a process argument.
- Give Suite and Frappe separate Stalwart app passwords.
- Preserve the current working `info@dehati.ir` login and mailbox data.
- Do not duplicate Email Queue, Communication, Email Template, or Unhandled Email in Vue.
- Do not claim external delivery is production-ready before HostIran DNS and PTR are correct.
- Keep canonical member `info@dehati.ir` visible exactly once even when Administrator shares its JMAP account.
- Keep email addresses, domains, URLs, DNS values, headers, and identifiers LTR inside the Persian UI.
- Use Peyda for Suite UI typography.
- Work and commit on `develop`; never place host configuration or secrets in Git.

---

### Task 1: Reproduce And Repair Tabs Compatibility

**Files:**
- Create: `frontend/src/utils/tabDefinitions.ts`
- Create: `frontend/src/utils/tabDefinitions.test.ts`
- Modify: `frontend/src/apps/mail/pages/dashboard/MembersView.vue`
- Modify: `frontend/src/apps/mail/pages/MailExchangesView.vue`
- Modify: `frontend/src/apps/mail/pages/CalendarExchangesView.vue`
- Modify: `frontend/src/apps/mail/pages/ContactsExchangesView.vue`
- Modify: `frontend/src/apps/mail/components/Modals/FolderModal.vue`
- Modify: every other Suite `Tabs` usage whose tab objects have no `value`

**Interfaces:**
- Produces: `indexedTabs<T>(tabs): Array<T & { value: number }>` for numeric `v-model` tabs.
- Consumes: frappe-ui Tabs, which requires a stable `value` on every tab.

- [ ] **Step 1: Write the failing helper test**

```ts
import { describe, expect, it } from 'vitest'
import { indexedTabs } from './tabDefinitions'

describe('indexedTabs', () => {
  it('adds stable numeric values without changing tab metadata', () => {
    const tabs = indexedTabs([{ label: 'Users' }, { label: 'Invites', disabled: true }])
    expect(tabs).toEqual([
      { label: 'Users', value: 0 },
      { label: 'Invites', disabled: true, value: 1 },
    ])
  })
})
```

- [ ] **Step 2: Verify RED**

Run: `yarn --cwd frontend vitest run src/utils/tabDefinitions.test.ts`

Expected: FAIL because `tabDefinitions` does not exist.

- [ ] **Step 3: Implement the helper**

```ts
export const indexedTabs = <T extends Record<string, unknown>>(tabs: readonly T[]) =>
  tabs.map((tab, value) => ({ ...tab, value }))
```

- [ ] **Step 4: Convert obsolete tab definitions**

Import `indexedTabs` and wrap numeric tab arrays. For Members:

```ts
const MEMBER_TABS = indexedTabs([
  { label: __('Users'), icon: Users },
  { label: __('Invites'), icon: Mails },
])
```

Bind `:tabs="MEMBER_TABS"`. Apply the same pattern to every numeric Suite Tabs model found by the audit. Existing semantic string models keep explicit string `value` fields instead.

- [ ] **Step 5: Verify GREEN and audit source**

Run:

```bash
yarn --cwd frontend vitest run src/utils/tabDefinitions.test.ts
rg -n "<Tabs|:tabs" frontend/src -g '*.vue'
```

Expected: helper test passes and every bound tab list supplies values directly or through `indexedTabs`.

- [ ] **Step 6: Commit**

```bash
git add frontend/src/utils frontend/src/apps
git commit -m "fix(ui): restore Suite tab panels"
```

---

### Task 2: Mail Navigation And Canonical Members

**Files:**
- Modify: `frontend/src/apps/mail/components/AppSidebar.vue`
- Modify: `frontend/src/apps/mail/router.ts`
- Modify: `frontend/src/apps/mail/pages/dashboard/UsersView.vue`
- Modify: `suite/mail/api/admin.py`
- Test: `frontend/src/apps/mail/routes.test.ts`
- Test: `suite/mail/tests/test_admin_members.py`

**Interfaces:**
- Produces: explicit Mailbox and Administration navigation destinations.
- Produces: `get_members()` rows only for canonical mailbox users, not shared viewers.

- [ ] **Step 1: Add failing backend coverage**

Extend `test_admin_members.py` with a shared viewer linked to the same JMAP account and assert:

```py
members = get_members()
assert [row["name"] for row in members].count(primary.email) == 1
assert shared_viewer.email not in [row["name"] for row in members]
```

Run the targeted test and confirm it fails because the shared viewer is currently selected through `User Settings.username`.

- [ ] **Step 2: Filter canonical members**

Make member selection require the Frappe user name to equal the mailbox username while retaining users that own independent mailboxes:

```py
.where(USER_SETTINGS.username.isnotnull())
.where(USER.name == USER_SETTINGS.username)
```

- [ ] **Step 3: Add route assertions**

Extend `routes.test.ts` to assert `/mail` resolves through `mail-root-shortcut` and `/mail/dashboard/members` resolves to `mail-members`.

- [ ] **Step 4: Add explicit navigation**

Add a translated `Mailbox` action targeting `mail-root-shortcut` for JMAP-configured users and retain `Administration`/overview for Suite admins. When no JMAP account exists, show a translated explanatory empty state instead of a blank body.

- [ ] **Step 5: Run tests**

```bash
yarn --cwd frontend vitest run src/apps/mail/routes.test.ts
bench --site dehati.ir run-tests --app suite --module suite.mail.tests.test_admin_members
```

Expected: all targeted tests pass and no test-created Stalwart principals remain after cleanup.

- [ ] **Step 6: Commit**

```bash
git add frontend/src/apps/mail suite/mail/api/admin.py suite/mail/tests/test_admin_members.py
git commit -m "fix(mail): separate mailbox navigation from administration"
```

---

### Task 3: Complete Persian Mail Coverage And RTL

**Files:**
- Create: `scripts/audit_persian_mail.py`
- Create: `scripts/persian_mail_overrides.py`
- Modify: `scripts/apply_persian_overrides.py`
- Modify: `suite/locale/fa.po`
- Modify: Mail Vue/TypeScript files containing direct visible strings
- Modify: `frontend/src/index.css` or Mail-scoped styles only where direction isolation is required
- Test: `suite/api/test_translations.py`
- Test: `frontend/src/boot/translation.test.ts`

**Interfaces:**
- Produces: a deterministic audit with `missing_or_empty=0`, `duplicates=0`, and `placeholder_mismatches=0` for Mail runtime keys.
- Consumes: static `__()` calls under `frontend/src/apps/mail` and the shared `suite/locale/fa.po` catalogue.

- [ ] **Step 1: Write the failing audit**

The script extracts literal `__()` keys from Mail `.vue` and `.ts` files, parses the PO catalogue, and exits non-zero when a key is absent, empty, duplicated, or has different `{0}` placeholders.

Run: `python scripts/audit_persian_mail.py`

Expected before implementation: FAIL with approximately 942 missing or empty keys.

- [ ] **Step 2: Extract direct visible text**

Convert hard-coded labels, placeholders, empty states, toasts, dialog text, and errors in Mail to `__()`. Do not translate protocol tokens or data values.

- [ ] **Step 3: Add reviewed Mail overrides**

Store reviewed Persian translations in `PERSIAN_MAIL_OVERRIDES` and merge it after existing overrides:

```py
overrides = {
    **PERSIAN_OVERRIDES,
    **CORE_VISIBLE_UX_OVERRIDES,
    **PERSIAN_MAIL_OVERRIDES,
}
```

Preserve all placeholders exactly and use consistent terminology for mailbox, member, domain, queue, report, identity, alias, and delivery.

- [ ] **Step 4: Add targeted RTL isolation**

Apply `dir="ltr"` or logical CSS to addresses, URLs, DNS values, headers, source, and identifiers. Do not mirror icons whose meaning is directional unless the action itself reverses in RTL.

- [ ] **Step 5: Synchronize and verify**

```bash
python scripts/apply_persian_overrides.py
python scripts/apply_persian_overrides.py --check
python scripts/audit_persian_mail.py
yarn --cwd frontend vitest run src/boot/translation.test.ts
```

Expected: zero missing keys, duplicates, and placeholder mismatches.

- [ ] **Step 6: Commit**

```bash
git add scripts suite/locale/fa.po frontend/src/apps/mail frontend/src/index.css
git commit -m "feat(i18n): complete Persian Suite Mail experience"
```

---

### Task 4: Share The Mailbox With Administrator

**Files:**
- Modify live `User Settings`, `User Account`, and JMAP account state on `dehati.ir` only.
- Do not create or modify a secret-bearing repository file.

**Interfaces:**
- Consumes: existing JMAP account `c` and mailbox `info@dehati.ir`.
- Produces: Administrator JMAP access with a dedicated app password.

- [ ] **Step 1: Capture idempotent pre-state**

Verify Administrator has no `User Account` mapping and record the existing canonical `info@dehati.ir` mapping without printing encrypted fields.

- [ ] **Step 2: Create a dedicated app password**

Run inside a Frappe transaction with Stalwart credentials loaded through root-only environment. Call `create_app_password("info@dehati.ir", "Suite Administrator access")`; assign it directly to Administrator's Password field without printing it.

- [ ] **Step 3: Configure Administrator**

Set Administrator `User Settings.username = "info@dehati.ir"`, save the encrypted app password, and create exactly one `User Account` mapping from Administrator to account `c` using Administrator's User Settings name.

- [ ] **Step 4: Verify and commit transaction**

As Administrator, assert `get_user_info().is_jmap_configured`, account `c`, seven standard mailboxes, identity `info@dehati.ir`, and Compose submission to a local self-test. Commit only after all checks succeed.

---

### Task 5: Configure Native Frappe Email

**Files:**
- Modify live `Email Account` state on `dehati.ir` only.

**Interfaces:**
- Produces: default Frappe outgoing account `info@dehati.ir` over authenticated SMTP SSL.
- Optionally produces: controlled IMAP-to-Communication import after compatibility verification.

- [ ] **Step 1: Create a dedicated transport credential**

Create a separate Stalwart app password described as `Frappe ERP transport`. Keep it only in memory until assigned to the Frappe Password field.

- [ ] **Step 2: Create or update Email Account**

Configure `info@dehati.ir` with SMTP `mail.dehati.ir:465`, SSL, authentication, enabled outgoing, and default outgoing. Remove the default outgoing flag from `Jobs` without deleting it.

- [ ] **Step 3: Test Frappe transactional sending**

Queue one identifiable message to `info@dehati.ir`, run the queue worker, and verify:

- Email Queue reaches `Sent`.
- Communication is created when the send path normally creates one.
- The message appears in Suite Inbox and Sent or the documented transport archive location.

- [ ] **Step 4: Test IMAP non-destructively**

Send one local message with a unique subject, enable incoming only for the controlled check, fetch once, and verify the original remains visible in Suite while one Communication is created. Keep incoming enabled only if both conditions hold; otherwise disable it and document outgoing-only operation.

---

### Task 6: Build, Deploy, And End-To-End Verification

**Files:**
- Replace generated files under `suite/public/frontend/` through the normal Vite build.
- Back up the previous generated frontend outside Git before deployment.

**Interfaces:**
- Consumes: completed frontend source, translations, and live integration.
- Produces: deployed Suite frontend and verification report.

- [ ] **Step 1: Record build provenance**

Record branch, commit, lockfile hash, Node version, and current `MembersView` asset hash. Confirm source and generated assets come from the same checkout.

- [ ] **Step 2: Run targeted and complete tests**

```bash
yarn --cwd frontend test
python scripts/apply_persian_overrides.py --check
python scripts/audit_persian_mail.py
git diff --check
```

Expected: all changed-area tests pass. Any pre-existing WebCrypto failure must be reproduced against the untouched base and reported separately, never described as passing.

- [ ] **Step 3: Build with sufficient memory**

```bash
NODE_OPTIONS='--max-old-space-size=6144' yarn --cwd frontend build
```

Expected: Vite and service-worker builds exit zero and write a new manifest and Members chunk.

- [ ] **Step 4: Deploy atomically and clear caches**

Back up the current public frontend, replace it only after a successful build, clear Frappe/Redis caches, and restart only the backend services required to load changed Python code. Do not restart Stalwart or the ERP database.

- [ ] **Step 5: Run authenticated smoke tests**

Verify as Administrator:

- `/mail` renders Inbox and Compose.
- `/mail/dashboard/members` renders one canonical `info@dehati.ir` row.
- Compose sends a unique self-test visible in Inbox.
- Frappe SMTP sends a transactional self-test.
- the interface is Persian and RTL on desktop and mobile.

Also verify `https://dehati.ir/api/method/ping`, Stalwart health, SMTP/IMAP TLS, service worker activation, and no new 404 assets.

- [ ] **Step 6: Commit generated/source state and push**

Commit only tracked source/generated files required by repository policy, run `git status --short --branch`, and push `develop` after verification. Never add backup files or secrets.
