# Payam Yar Complete Persian and RTL Design

## Goal

Make Payam Yar usable end-to-end in Persian for regular users and administrators. All product chrome, onboarding, forms, dialogs, status messages, empty states, errors, and administrative workflows must have Persian translations and render correctly in RTL mode.

The direction of message content must remain content-aware. Received email bodies, the compose editor, email addresses, URLs, code, DNS values, DKIM keys, and other technical values must not be forcibly mirrored.

## Scope

### Payam Yar user experience

- Login, signup, invitation setup, password reset, and initial setup states.
- Mailbox navigation, thread lists, search, screener, outbox, contacts, address books, and profile.
- Compose, reply, forward, scheduling, attachments, signatures, settings, imports, exports, and automation.
- Toasts, validation errors, server errors, confirmations, empty states, loading states, and accessibility labels.
- Desktop and mobile layouts.

### Administration

- Overview, members, invitations, groups, mailing lists, roles, OAuth clients, domains, and DKIM.
- Queued messages, delivery tests, inbound and outbound reports, logs, and actions.
- Every administration dialog, table header, filter, badge, error, and action.
- A visible, permission-aware Frappe Email tools section.

### Shared onboarding

The Suite onboarding shell is included because it is the first-run entry point used before opening Payam Yar. Its visible strings and direction must follow the active Persian locale.

### Native Frappe Email tools

Payam Yar will expose stable links for:

- Email Account
- Communication
- Email Queue
- Email Template
- Unhandled Email

These links will remain native Desk routes instead of duplicating Frappe functionality inside the SPA. They will be visible only to users who can access the administrative area. A Desk workspace or equivalent discoverable entry will expose the same tools without modifying Frappe core.

## Translation Architecture

The existing `suite/locale/fa.po` catalogue remains the source of runtime Persian translations. Product-specific overrides remain deterministic through the checked-in override scripts.

The current audit only verifies literal keys already wrapped in `__()`. It will be extended to detect likely user-facing strings that bypass translation, including:

- Vue template text nodes.
- Literal `label`, `title`, `placeholder`, `description`, `message`, tooltip, and accessibility values.
- User-facing strings assembled dynamically in TypeScript.
- Administrative and onboarding files outside the current Mail-only scan.

Technical identifiers, API payload values, protocol names, test fixtures, comments, and logging-only text are excluded. Every runtime key must have a non-empty Persian translation with matching placeholders and no duplicate catalogue entries.

Server-originated messages owned by Suite Mail will use translatable source strings. Messages owned by Frappe itself will use Frappe's existing Persian catalogue rather than being patched in Frappe core.

## RTL Architecture

The active locale endpoint remains responsible for setting `lang` and `dir` on the document root. Persian resolves to `dir="rtl"` before the application becomes interactive.

Layout rules will use logical properties and RTL-aware utilities. Directional controls such as back/forward arrows and slide transitions will be reviewed so their meaning follows navigation rather than a hard-coded physical side.

The following content is explicitly isolated from global RTL:

- Email addresses, URLs, telephone numbers, numeric identifiers, code, and preformatted text: LTR.
- DNS records, SPF, DKIM, DMARC, tokens, and server values: LTR with bidi isolation.
- Received email HTML and plain text: preserve sender content or use automatic direction.
- Compose subject and body: automatic direction based on content; interface controls remain RTL.

This prevents Persian chrome from corrupting English messages or technical data.

## Frappe Email Discoverability

The existing route constants are retained. Their presentation will be changed from a fragile sidebar-only block to a reusable, permission-aware definition used by:

- The Payam Yar administration sidebar.
- The administration overview or tools surface.
- A Suite-owned Desk workspace/shortcut surface.

The implementation will test that every route is present and points to the canonical Desk URL. It will not recreate Email Account, Communication, Email Queue, Email Template, or Unhandled Email inside Suite.

## Cache and Deployment

The frontend build emits hashed assets and a Mail service worker. Deployment must:

1. Generate the Persian catalogue and verify it is deterministic.
2. Run backend and frontend tests.
3. Build production assets.
4. Run site migration and clear Frappe cache.
5. Restart affected Frappe services.
6. Verify the live HTML references the new hashes.
7. Ensure the service worker update path does not keep an obsolete English bundle active.

No Stalwart restart or mail data migration is required unless a server-side Mail schema change is introduced.

## Testing

Automated checks will cover:

- No missing, duplicate, or placeholder-mismatched Persian runtime keys.
- Detection of untranslated direct UI strings in the agreed source scope.
- Persian locale sets document RTL.
- Technical and message-content direction exceptions.
- Frappe Email tool labels and canonical routes.
- Onboarding and administration translation keys.
- Existing Mail frontend and backend regressions.
- Production build completion.

Live verification on `dehati.ir` will cover the onboarding entry, Mail inbox, compose flow, settings, administration dashboard, member dialog, domain/DKIM screens, and Frappe Email links on desktop and mobile-sized layouts.

## Non-Goals

- Translating email bodies received from other people.
- Translating protocol names or changing DNS/DKIM data.
- Forking or directly editing Frappe core solely for labels.
- Reimplementing native Frappe Email DocTypes inside Payam Yar.
- Forcing RTL on English email composition or received content.

## Acceptance Criteria

- A Persian user can complete onboarding and all primary Mail tasks without visible English product text.
- A Persian administrator can complete all Payam Yar administration workflows without visible English product text, excluding defined technical terms and values.
- All application chrome is RTL while email content and technical values retain a readable direction.
- The five native Frappe Email tools are visible, translated, permission-aware, and open their correct Desk routes.
- Translation audits, tests, production build, migration, and live asset checks pass.
- Changes are committed and pushed to `develop` without modifying Frappe core.
