# Suite Branch Integration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Produce one tested `develop` branch containing the current Frappe Suite code, Sepehr's Persian localization and server fallbacks, and the recoverable changes from the server snapshot.

**Architecture:** Use `upstream/develop` as the source-code baseline because it is 1,643 commits newer than the fork base. Record both fork histories as merge parents, then port their functional changes onto the current architecture instead of restoring files that upstream intentionally deleted. Keep translations in the Suite `fa.po` catalogue, bootstrap Persian locale/RTL centrally, and preserve Peyda as a self-contained font asset.

**Tech Stack:** Git, Frappe Suite, Vue 3, Vite, Vitest, Python/Frappe locale catalogues.

## Global Constraints

- Final public branch is `develop`; do not create or restore `main`.
- Preserve upstream implementations when a component was removed, renamed, or redesigned.
- Preserve user-facing Persian translations, RTL bootstrap, Peyda fonts, boot fallbacks, and optional-dependency safeguards.
- Do not deploy to `dehati.ir` until tests and production build pass in the isolated worktree.
- Do not remove `server-snapshot-20260825` until the deployed result is verified.

---

### Task 1: Unify Git Histories

**Files:**
- Modify: Git history only

**Interfaces:**
- Consumes: `upstream/develop`, `origin/develop`, `origin/server-snapshot-20260825`
- Produces: `integrate/suite-final` containing both branch histories

- [x] **Step 1: Record the customized fork history**

Run: `git merge --no-ff -s ours origin/develop -m "Merge customized develop history into current Suite"`

Expected: merge commit with `origin/develop` as the second parent and the current upstream tree unchanged.

- [x] **Step 2: Record the independent server snapshot history**

Run: `git merge --no-ff -s ours --allow-unrelated-histories origin/server-snapshot-20260825 -m "Merge server snapshot history"`

Expected: merge commit with the snapshot as the second parent and no source-code regression.

### Task 2: Port Server Compatibility Fixes

**Files:**
- Modify only when the current upstream still lacks the behavior: `suite/mail/install.py`, `frontend/src/apps/mail/utils/pushNotificationConfig.ts`, `frontend/src/apps/mail/sw.ts`, `frontend/src/apps/meet/composables/useMeetingPreviewPresence.ts`, `suite/drive/api/storage.py`, `suite/www/suite.py`, `suite/calendar/api/__init__.py`
- Test: nearest current unit tests for each retained behavior

**Interfaces:**
- Consumes: behavior from commits `3fd424e53`, `6bda81a01`, and the 25 modified snapshot files relative to upstream commit `ad6c84baa`
- Produces: safe startup when optional DocTypes, Firebase configuration, team selection, SFU secret, or optional Python packages are absent

- [x] **Step 1: Compare each old fix with current upstream**

Run targeted `git show` and `git diff` checks. Skip a patch only when current upstream already implements the same guard or the affected feature no longer exists.

- [x] **Step 2: Apply the minimum compatible changes and their tests**

Port the guard at the current call site, preserving current function signatures and data flow. Do not restore deleted components.

- [x] **Step 3: Run targeted tests**

Run the current Vitest/Python test files covering every retained guard and require zero failures.

### Task 3: Port Persian Locale, RTL, and Typography

**Files:**
- Create: `frontend/src/assets/fonts/Peyda-Regular.ttf`, `frontend/src/assets/fonts/Peyda-Medium.ttf`, `frontend/src/assets/fonts/Peyda-SemiBold.ttf`, `frontend/src/assets/fonts/Peyda-Bold.ttf`
- Create: `suite/locale/fa.po`, `scripts/apply_persian_overrides.py`, `scripts/persian_core_ux_overrides.py`, `scripts/persian_overrides.py`
- Modify: `frontend/src/boot/translation.ts`, `frontend/src/index.css`, `frontend/src/main.ts`, `frontend/src/router/index.ts`, `suite/api/__init__.py`
- Test: locale catalogue check plus frontend tests

**Interfaces:**
- Consumes: commits `b3bacf69b`, `069fc9024`, and `3d6985eaf`
- Produces: Persian catalogue loading, document `lang`/`dir` synchronization, Peyda typography, and translated visible strings

- [x] **Step 1: Restore catalogue assets and deterministic override scripts**

Restore the seven assets/scripts from `origin/develop`, then run `python3 scripts/apply_persian_overrides.py --check`.

- [x] **Step 2: Port central locale bootstrap onto current files**

Apply only the Persian locale, `dir=rtl`, and document-language behavior from `b3bacf69b`; retain current upstream router and boot logic.

- [x] **Step 3: Regenerate and validate the Persian catalogue**

Run the override script normally, then rerun it with `--check`. Require zero duplicate keys, zero placeholder mismatches, and no pending updates.

- [x] **Step 4: Audit visible source strings**

Compare the runtime keys from the three localization commits with current source. Add missing `__()` wrappers only to components that still exist; do not recreate deleted components.

### Task 4: Verification and Publication

**Files:**
- Modify: `docs/superpowers/plans/2026-08-27-suite-branch-integration.md` checkbox state

**Interfaces:**
- Consumes: integrated source tree
- Produces: tested GitHub `develop` and deployed assets on `dehati.ir`

- [x] **Step 1: Run integrity checks**

Run `git diff --check`, scan for conflict markers, and confirm both old branch tips are ancestors of HEAD.

- [x] **Step 2: Run full frontend tests**

Run: `yarn workspace @suite/frontend test`

Expected: at least the baseline 2,121 tests pass with no new failures.

- [x] **Step 3: Run production build**

Run: `NODE_OPTIONS='--max-old-space-size=6144' yarn build`

Expected: Vite and service-worker builds exit successfully.

- [x] **Step 4: Review the integrated diff**

Review changes against `upstream/develop`; reject stale files, unresolved English core strings, leaked secrets, generated build output, and unrelated refactors.

- [x] **Step 5: Publish and deploy**

Push the verified integration commit to `origin/develop`, update the server checkout to `develop`, rebuild assets, clear cache, restart only Suite/Frappe web services, and smoke-test `/suite`, `/drive`, `/meet`, `/writer`, `/slides`, `/sheets`, `/mail`, and `/calendar` for HTTP 200.
