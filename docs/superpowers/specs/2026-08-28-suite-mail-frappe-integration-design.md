# Suite Mail And Frappe Email Integration Design

## Goal

Make `info@dehati.ir` the single mail identity for the site while preserving the correct separation of responsibilities:

- Stalwart remains the authoritative mail server.
- Suite Mail remains the interactive mailbox and domain-administration client.
- Frappe Email remains the transactional and ERP-document mail subsystem.

The work also restores the currently broken Suite Mail interface, completes its Persian localization, and verifies that the deployed frontend was built from the intended source.

## Current Findings

### Blank dashboard pages

The Members API is healthy for both `Administrator` and `info@dehati.ir`; it returns the active `info@dehati.ir` member. The blank Members body is a frontend regression.

The installed `frappe-ui` Tabs component requires every tab to have a stable `value`. Suite still passes arrays containing only `label` and `icon` in several places. On Members, both tabs therefore resolve to `undefined`, the numeric `v-model` cannot select a panel, and the page body stays empty. The deployed `MembersView` bundle contains this incompatible source, so the problem is in the source/build input rather than a failed file upload.

Affected usages must be audited across Mail and the rest of Suite, not patched only in Members.

### Mailbox access

`/mail/dashboard` is the administrative dashboard. It intentionally has no Compose button. `/mail` resolves to the active JMAP mailbox and owns Compose. The current browser session is `Administrator`, which is a Suite administrator but has no JMAP account mapping, while `info@dehati.ir` has the working mailbox.

### Localization

The Mail frontend currently contains 1,267 statically extractable runtime translation keys. Only 325 have non-empty Persian translations; 942 are missing or empty. This is 25.7 percent coverage before accounting for direct user-facing strings that bypass `__()`.

### Frappe Email

The site has only a disabled placeholder `jobs@example.com` Email Account marked as default outgoing. ERP transactional email is therefore not correctly configured. Email Queue, Communication, Email Template, and Unhandled Email are native Frappe subsystems and should be integrated, not copied into Suite.

## Architecture

### Shared identity, separate clients

Stalwart owns the mailbox and credentials for `info@dehati.ir`. Each client receives a separate app password:

- Suite `info@dehati.ir` JMAP connection
- Administrator Suite JMAP connection
- Frappe Email Account SMTP/IMAP connection

No Stalwart administrator or recovery password is reused by a client.

### Administrator mailbox access

Administrator receives a `User Account` mapping to the existing personal JMAP account and its own JMAP app password in Administrator's encrypted `User Settings`. This allows the existing Desk session to open `/mail`, read the mailbox, and compose mail without logging in as a second Frappe user.

The canonical mailbox member remains `info@dehati.ir`. Shared viewers such as Administrator must not appear as duplicate mailbox members in the admin directory. Member listing will distinguish canonical mailbox users from users granted access to an existing account.

### Frappe Email Account

Create one enabled Email Account for `info@dehati.ir`:

- SMTP host: `mail.dehati.ir`
- SMTP port: `465`
- SSL enabled
- Default outgoing enabled
- Dedicated Stalwart app password stored through Frappe's Password field

Incoming synchronization is enabled only after a controlled compatibility test confirms that Frappe can fetch without deleting mail or disrupting Suite state. If enabled, it uses IMAP on port `993` with SSL and imports mail into Communication. This provides ERP linking and inbound routing while Suite continues to display the authoritative mailbox.

The placeholder `jobs@example.com` account loses its default flag. It is not deleted unless it has no references and removal is verified safe.

### Frappe feature coverage

The integration preserves these native responsibilities:

- Email Account: transport and inbound routing
- Email Queue: transactional retries and delivery status
- Communication: ERP document timeline and correspondence
- Email Template: reusable ERP messages
- Unhandled Email: inbound messages Frappe could not route
- Notifications and document email: native Frappe send path

Suite provides the mailbox, folders, Compose, identities, signatures, contacts, screening, aliases, groups, mailing lists, DKIM, delivery reports, and domain administration.

Suite will expose clear links and status summaries for the native Frappe email tools where that improves discoverability. It will not duplicate their business logic or database models.

## Frontend Repair

### Tabs compatibility

Every Suite `Tabs` array receives explicit stable values. Existing numeric models use `0`, `1`, and so on; string models use semantic values. Route-backed tabs continue to derive their selected value from the route.

Regression tests cover:

- Members and Invites render their panel.
- Mail, Calendar, and Contacts exchange tabs render Import and Export.
- Folder settings render General and Automation.
- Other Suite applications using the same obsolete pattern are corrected.

### Navigation

The admin dashboard clearly exposes two destinations:

- `Mailbox` routes to `/mail` and is available when the current user has JMAP access.
- `Administration` routes to `/mail/dashboard` and is available to Suite administrators.

The UI must not imply that the administration dashboard is the Inbox. Empty or unavailable account states display a Persian diagnostic instead of a blank body.

### Persian and RTL

All user-visible Mail frontend strings are passed through `__()`. The Persian catalogue covers all extracted Mail runtime keys with placeholder parity and no duplicate entries.

RTL is applied to shell, dashboard, lists, dialogs, Compose, recipients, search, settings, reports, and mobile views. Direction-sensitive content remains LTR:

- email addresses
- domains and URLs
- message headers
- code and raw source
- DNS record values
- cryptographic identifiers

Peyda remains the Suite font. Technical tokens use a suitable monospace fallback when needed.

## Build And Deployment

The build must run from `develop` at the expected commit with the pinned dependency lockfile. Before deployment, verification records:

- Git commit and branch
- dependency install result
- translation catalogue checks
- targeted frontend tests
- all frontend tests
- transformed module count
- final build exit status
- generated manifest and Members chunk hashes

Deployment replaces Suite public frontend assets atomically, clears Frappe and Redis caches, and updates or invalidates the Suite service worker. Existing ERP containers are not rebuilt or restarted unless a backend code change requires it; targeted service restarts are preferred.

## Error Handling And Rollback

- Database changes are idempotent and committed only after the corresponding Stalwart operation succeeds.
- New app passwords are never printed, committed, or placed in process arguments.
- Existing working `info@dehati.ir` credentials remain valid during rollout.
- The current public frontend directory is backed up before replacement.
- If the new frontend fails smoke tests, restore the prior assets without rolling back Stalwart mail data.
- If Frappe incoming synchronization changes mailbox state unexpectedly, disable incoming while keeping outgoing enabled.

## Verification

### Backend

- Administrator and `info@dehati.ir` both resolve JMAP account `c`.
- `get_members` returns the canonical `info@dehati.ir` member exactly once.
- JMAP discovery, identities, mailboxes, and push subscriptions work.
- Frappe Email Account sends through authenticated SMTP.
- A Frappe transactional test reaches the external SMTP submission path and records queue/Communication state.
- Controlled inbound mail remains visible in Suite and, if IMAP integration is enabled, appears once in Communication.

### Frontend

- `/mail` renders Inbox and Compose for Administrator.
- `/mail/dashboard/members` renders `info@dehati.ir`.
- Compose sends a self-test that appears in Inbox and Sent.
- Mail admin pages no longer render blank tab panels.
- Persian Mail runtime catalogue has no missing keys or placeholder mismatches.
- Desktop and mobile RTL smoke tests cover mailbox, Compose, Members, settings, and domain DNS views.

### Isolation

- `https://dehati.ir/api/method/ping` remains healthy.
- ERP Desk remains accessible.
- Stalwart remains healthy after the deployment.
- No secret appears in Git diff, build output, or deployment logs.

## Non-Goals

- Reimplementing Email Queue, Communication, Email Template, or Unhandled Email inside Vue.
- Replacing Stalwart with Frappe's mail transport.
- Publishing DNS or claiming external deliverability before HostIran MX, SPF, DKIM, DMARC, and PTR changes are visible publicly.
- Hiding genuine delivery errors caused by incomplete public DNS.
