# Payam Yar Mail Branding Design

## Goal

Present Suite Mail to end users as **پیام‌یار** in Persian and **Payam Yar** in English. Account invitation and verification emails must be Persian, right-to-left, and sent with the display name **مجموعه دهاتی**.

This is a display-branding change for Mail only. It does not rename Suite, Drive, Calendar, or other products.

## Branding Configuration

Add a Branding section to the singleton `Mail Settings` DocType with these database-backed fields:

- `mail_product_name_fa`, default `پیام‌یار`
- `mail_product_name_en`, default `Payam Yar`
- `mail_sender_name`, default `مجموعه دهاتی`

Backend mail helpers read the cached Mail Settings values and fall back to these defaults when a field is empty. This keeps transactional mail operational during migration and lets administrators update the visible brand without code changes.

The sender email address remains the address selected by Frappe's outgoing Email Account. The branding layer changes only its display name. It must not embed credentials or duplicate SMTP configuration.

## Transactional Emails

Replace the generic Frappe email shell for Mail account invitations and signup verification codes with a dedicated `payam_yar_account_email` template.

The template must:

- use UTF-8 Persian copy and `dir="rtl"`;
- use email-client-safe inline styles and a mobile-friendly single-column layout;
- show the product name `پیام‌یار` and sender organization `مجموعه دهاتی`;
- provide a clear primary action for invitations;
- include the raw verification URL as a fallback;
- render verification codes with left-to-right isolation;
- avoid external fonts, scripts, and remote tracking resources.

Invitation content:

- Subject: `دعوت‌نامه عضویت در پیام‌یار`
- Title: `دعوت‌نامه عضویت در پیام‌یار`
- Explain that the recipient was invited by the Dehati organization.
- Action: `تأیید و ساخت حساب`
- State that an unexpected invitation can be ignored.

Verification content:

- Subject: `کد تأیید پیام‌یار`
- Title: `کد تأیید ایمیل`
- Show the one-time code and its expiry in minutes.
- State that an unexpected request can be ignored.

Both send paths explicitly pass a standards-compliant formatted sender such as `مجموعه دهاتی <info@dehati.ir>`. The address comes from Frappe's active outgoing Email Account and the display name comes from Mail Settings. Existing recipient addresses, request keys, expiry behavior, audit logging, and synchronous delivery behavior remain unchanged.

## Visible Mail UI

Replace end-user-visible `Frappe Mail` branding in the Mail application with locale-aware branding:

- Persian UI: `پیام‌یار`
- Other locales: `Payam Yar`
- Login and signup surfaces
- Install prompt
- Mail PWA manifest name and short name
- Mail email footers and other Mail-owned notification templates

Static assets that cannot read database settings use the approved display constants above. Runtime UI text uses the existing translation system.

## Compatibility Boundaries

Do not rename internal identifiers or persisted paths, including:

- Python package and module names;
- DocType names;
- route names and API paths;
- the existing `Home/Frappe Mail` file folder;
- database records whose names are technical keys;
- protocol metadata required for compatibility.

Developer comments and historical test descriptions need not be rebranded unless they surface to users. This minimizes divergence from upstream and protects existing data.

## Migration and Deployment

The DocType schema change is applied with the normal site migration. Default branding values are stored in `Mail Settings` so the deployed site is immediately configured without manual data entry. Existing outgoing email account configuration remains authoritative for the sender address.

Deployment order:

1. update the app on `develop`;
2. run backend and frontend tests;
3. migrate `dehati.ir`;
4. build frontend assets;
5. clear caches and restart services;
6. send a test invitation and inspect the queued message headers and rendered body;
7. push the verified commit to the fork's `develop` branch.

## Error Handling

- Empty branding settings use safe defaults.
- Missing outgoing email configuration continues to produce Frappe's existing delivery error; branding must not hide it.
- Template rendering failures must be covered by tests and must not fall back silently to English content.
- User-provided and database-provided text is escaped by the template unless a value is explicitly trusted markup.

## Testing

Add focused tests that verify:

- invitation subject, template, Persian content, verification link, and sender display name;
- OTP subject, Persian content, code, expiry, and sender display name;
- fallback branding when settings are empty;
- the account request and audit behavior remains unchanged;
- no visible `Frappe Mail` remains in scoped Mail UI and Mail-owned email templates;
- PWA manifest identifies the app as `Payam Yar`;
- the Persian catalog has valid placeholders and no duplicate entries introduced by this work.

Run the targeted backend tests, frontend tests related to Mail branding, translation checks, the production frontend build, and a live invitation smoke test on `dehati.ir`.

## Success Criteria

- A recipient sees the sender as `مجموعه دهاتی` using the configured outgoing email address.
- Invitation and verification emails are fully Persian and render right-to-left.
- The visible Mail product name is `پیام‌یار` in Persian and `Payam Yar` otherwise.
- Existing accounts, messages, attachments, and the `Home/Frappe Mail` folder continue to work.
- The deployed site passes the focused tests and live invitation smoke test.
