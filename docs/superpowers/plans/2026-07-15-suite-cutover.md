# Suite Cutover Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace standalone productivity apps on `dehati.ir` with `suite` from `sepehrsariaslani/suite`.

**Architecture:** Keep the old app directories available until `suite` is fully installed and migrated. Perform a site backup, validate the unified build, cut over the site, then clean up bench state.

**Tech Stack:** Frappe Bench v16, Docker containers, Python backend app, Vite/Vue frontend SPA, MariaDB site backup and migrate flow.

## Global Constraints

- Site target is exactly `dehati.ir`.
- Source branch is exactly `develop` from `git@github.com:sepehrsariaslani/suite.git`.
- Standalone Persian customizations are intentionally discarded.
- Do not delete old app directories before `suite` is installed and validated.
- Build and runtime verification are required before declaring cutover successful.

---

### Task 1: Preflight And Bench Inventory

**Files:**
- Modify: `docs/superpowers/plans/2026-07-15-suite-cutover.md`
- Inspect: `/home/sepehr/den-v16-docker/sites/apps.txt`
- Inspect: `/home/sepehr/den-v16-docker/apps/suite/pyproject.toml`
- Inspect: `/home/sepehr/den-v16-docker/apps/suite/package.json`

**Interfaces:**
- Consumes: existing bench at `/home/sepehr/den-v16-docker`
- Produces: confirmed source-of-truth list of installed apps and build prerequisites

- [ ] **Step 1: Verify current site app state**

Run:

```bash
docker exec den-v16-backend bash -lc 'cd /home/frappe/frappe-bench && bench --site dehati.ir list-apps'
```

Expected: app list clearly shows whether `slides`, `sheets`, `drive`, `writer`, or `suite` are installed.

- [ ] **Step 2: Verify suite branch and repo health**

Run:

```bash
git -C /home/sepehr/den-v16-docker/apps/suite branch --show-current
git -C /home/sepehr/den-v16-docker/apps/suite status --short
```

Expected: branch is `develop`, worktree is clean enough to proceed.

- [ ] **Step 3: Inspect build and hook entry points**

Run:

```bash
sed -n '1,220p' /home/sepehr/den-v16-docker/apps/suite/pyproject.toml
sed -n '1,220p' /home/sepehr/den-v16-docker/apps/suite/package.json
sed -n '1,220p' /home/sepehr/den-v16-docker/apps/suite/suite/hooks.py
```

Expected: dependencies and asset build commands are known before cutover.

- [ ] **Step 4: Commit if this task changed the plan**

```bash
git -C /home/sepehr/den-v16-docker/apps/suite add docs/superpowers/plans/2026-07-15-suite-cutover.md
git -C /home/sepehr/den-v16-docker/apps/suite commit -m "docs: add suite cutover plan"
```

### Task 2: Backup And Build Verification

**Files:**
- Create: backup artifacts under `/home/sepehr/den-v16-docker/sites`
- Inspect: `/home/sepehr/den-v16-docker/apps/suite/frontend`

**Interfaces:**
- Consumes: validated bench and site target
- Produces: rollback point and proof that `suite` assets can build

- [ ] **Step 1: Create fresh site backup**

Run:

```bash
docker exec den-v16-backend bash -lc 'cd /home/frappe/frappe-bench && bench --site dehati.ir backup --with-files'
```

Expected: backup completes successfully and creates fresh database and file archives.

- [ ] **Step 2: Install JS dependencies if required**

Run:

```bash
docker exec den-v16-backend bash -lc 'cd /home/frappe/frappe-bench/apps/suite/frontend && yarn install --frozen-lockfile || yarn install'
```

Expected: frontend dependencies are present without fatal errors.

- [ ] **Step 3: Verify suite frontend build before cutover**

Run:

```bash
docker exec den-v16-backend bash -lc 'cd /home/frappe/frappe-bench/apps/suite/frontend && yarn build'
```

Expected: build exits `0`.

- [ ] **Step 4: Commit if any repo files changed during setup**

```bash
git -C /home/sepehr/den-v16-docker/apps/suite status --short
```

Expected: either no repo diff, or intentional lock/config changes reviewed before proceeding.

### Task 3: Site Cutover

**Files:**
- Modify: `/home/sepehr/den-v16-docker/sites/apps.txt` if bench app references need update

**Interfaces:**
- Consumes: successful backup and successful build
- Produces: `suite` installed on `dehati.ir` and standalone apps removed from the site

- [ ] **Step 1: Uninstall standalone site apps if installed**

Run:

```bash
docker exec den-v16-backend bash -lc '
cd /home/frappe/frappe-bench &&
for app in drive writer slides sheets; do
  if bench --site dehati.ir list-apps | grep -qx "$app"; then
    bench --site dehati.ir uninstall-app "$app" --yes
  fi
done'
```

Expected: installed standalone productivity apps are removed from the site without deleting their directories.

- [ ] **Step 2: Register suite on the bench if needed**

Run:

```bash
docker exec den-v16-backend bash -lc 'cd /home/frappe/frappe-bench && grep -qx "suite" sites/apps.txt || echo suite >> sites/apps.txt'
```

Expected: `suite` is present in bench app registry.

- [ ] **Step 3: Install suite on the site**

Run:

```bash
docker exec den-v16-backend bash -lc 'cd /home/frappe/frappe-bench && bench --site dehati.ir install-app suite'
```

Expected: install completes successfully.

- [ ] **Step 4: Run migrate**

Run:

```bash
docker exec den-v16-backend bash -lc 'cd /home/frappe/frappe-bench && bench --site dehati.ir migrate'
```

Expected: migrate exits `0`.

- [ ] **Step 5: Build bench assets and clear cache**

Run:

```bash
docker exec den-v16-backend bash -lc 'cd /home/frappe/frappe-bench && bench build --app suite && bench --site dehati.ir clear-cache'
```

Expected: build exits `0`, cache clear exits `0`.

### Task 4: Runtime Validation

**Files:**
- Inspect runtime routes and installed app state

**Interfaces:**
- Consumes: migrated `suite` install
- Produces: confidence that the unified app works on the live site

- [ ] **Step 1: Restart app containers**

Run:

```bash
docker restart den-v16-backend den-v16-queue-short den-v16-queue-long den-v16-scheduler den-v16-websocket
```

Expected: all containers return to `Up` state.

- [ ] **Step 2: Verify installed app state after cutover**

Run:

```bash
docker exec den-v16-backend bash -lc 'cd /home/frappe/frappe-bench && bench --site dehati.ir list-apps'
```

Expected: `suite` is installed; standalone productivity apps are no longer installed.

- [ ] **Step 3: Smoke test suite routes**

Run:

```bash
curl -I https://dehati.ir/suite
curl -I https://dehati.ir/drive
curl -I https://dehati.ir/slides
curl -I https://dehati.ir/writer
curl -I https://dehati.ir/sheets
```

Expected: no 500 response on main suite routes.

- [ ] **Step 4: Validate desk boot does not hit module import errors**

Run:

```bash
docker exec den-v16-backend bash -lc 'cd /home/frappe/frappe-bench && bench --site dehati.ir console <<\"PY\"\nimport frappe\nprint(frappe.get_installed_apps())\nPY'
```

Expected: console opens cleanly and installed apps include `suite`.

### Task 5: Cleanup And Publish

**Files:**
- Remove: `/home/sepehr/den-v16-docker/apps/drive`
- Remove: `/home/sepehr/den-v16-docker/apps/writer`
- Remove: `/home/sepehr/den-v16-docker/apps/slides`
- Remove: `/home/sepehr/den-v16-docker/apps/sheets`

**Interfaces:**
- Consumes: successful runtime validation
- Produces: clean bench state and updated git history on `suite`

- [ ] **Step 1: Remove obsolete standalone app references only after validation**

Run:

```bash
python3 - <<'PY'
from pathlib import Path
apps = Path('/home/sepehr/den-v16-docker/sites/apps.txt')
lines = [line for line in apps.read_text().splitlines() if line not in {'drive','writer','slides','sheets'}]
apps.write_text('\n'.join(lines) + '\n')
PY
```

Expected: `sites/apps.txt` no longer references standalone productivity apps.

- [ ] **Step 2: Remove obsolete app directories**

Run:

```bash
rm -rf /home/sepehr/den-v16-docker/apps/drive
rm -rf /home/sepehr/den-v16-docker/apps/writer
rm -rf /home/sepehr/den-v16-docker/apps/slides
rm -rf /home/sepehr/den-v16-docker/apps/sheets
```

Expected: only `suite` remains as the productivity app source.

- [ ] **Step 3: Commit suite repo changes**

```bash
git -C /home/sepehr/den-v16-docker/apps/suite status --short
git -C /home/sepehr/den-v16-docker/apps/suite add -A
git -C /home/sepehr/den-v16-docker/apps/suite commit -m "chore: document suite cutover"
git -C /home/sepehr/den-v16-docker/apps/suite push origin develop
```

- [ ] **Step 4: Final verification**

Run:

```bash
docker exec den-v16-backend bash -lc 'cd /home/frappe/frappe-bench && bench --site dehati.ir list-apps'
```

Expected: final installed app list is stable and includes `suite`.
