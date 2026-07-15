# Suite Cutover Design

## Goal

Replace the separately managed productivity apps on `dehati.ir` with a single `suite`
app from `sepehrsariaslani/suite` on branch `develop`, while preserving site uptime as
much as possible and keeping a rollback path.

## Current State

- Bench root: `/home/sepehr/den-v16-docker`
- Site: `dehati.ir`
- Installed relevant apps on the site: `slides`, `sheets`
- Present on disk but not confirmed installed on the site: `drive`, `writer`
- Target app: `suite`, which consolidates `Drive`, `Slides`, `Writer`, `Sheets`,
  `Meet`, `Mail`, and `Calendar` into one backend app and one frontend SPA

## Decision

Use a clean cutover:

1. Bring `suite` into the bench and verify it can build.
2. Back up `dehati.ir`.
3. Uninstall the separate productivity apps from the site.
4. Install `suite` on the site.
5. Run migrate/build/clear-cache/restart.
6. Smoke-test the Suite launcher and product routes.
7. Remove obsolete standalone app directories and bench references only after a
   successful site cutover.

## Why This Approach

- It leaves one steady-state app instead of a mixed install with duplicated modules.
- It keeps rollback simple because the old app directories remain available until the
  new app is proven on the live site.
- It avoids trying to preserve low-value local customizations the user explicitly no
  longer cares about.

## Cutover Sequence

### 1. Preflight

- Confirm the `suite` fork is on `develop`
- Inspect `pyproject.toml`, `package.json`, `suite/hooks.py`, and `suite/patches.txt`
- Confirm which standalone apps are actually installed on `dehati.ir`
- Confirm bench build prerequisites inside `den-v16-backend`

### 2. Safety Snapshot

- Run a fresh site backup for database + files before uninstalling anything
- Record current installed-app state from the site and `sites/apps.txt`

### 3. Bench Preparation

- Add `suite` to the bench
- Install Python and JS dependencies if needed
- Run `yarn build` from `suite/frontend` or `bench build --app suite`

### 4. Site Cutover

- Uninstall standalone productivity apps from `dehati.ir`
- Install `suite` on `dehati.ir`
- Run `bench --site dehati.ir migrate`
- Rebuild assets and clear cache
- Restart relevant containers/processes

### 5. Validation

- Confirm `suite` is in installed apps
- Confirm old standalone apps are no longer installed on the site
- Smoke-test:
  - `/suite`
  - `/drive`
  - `/slides`
  - `/writer`
  - `/sheets`
- Confirm desk boot succeeds without import/module errors

### 6. Cleanup

- Remove obsolete app references from `sites/apps.txt`
- Remove obsolete app directories from `apps/` only after validation
- Keep backups intact for rollback

## Risks

### Data / uninstall risk

Standalone app uninstall hooks may drop metadata or records. This must be checked
before uninstall, and backup must be taken first.

### Module / route overlap

The site may have route, workspace, or module-name assumptions tied to old apps. The
validation phase must explicitly check desk boot and route access after migration.

### Asset/runtime mismatch

`suite` is a consolidated SPA. Old built assets or stale process memory can produce
false negatives. Cache clear and process restart are part of cutover, not optional.

## Rollback

If `suite` install or migrate fails:

1. Stop the cutover.
2. Keep old standalone app directories intact.
3. Restore site backup if uninstall side effects are not trivially reversible.
4. Reinstall previous standalone apps on `dehati.ir` if needed.
5. Rebuild assets and restart processes.

## Out of Scope

- Preserving or porting previous Persian customizations from `slides`, `drive`,
  `writer`, or `sheets`
- Extending `suite` functionality beyond getting the consolidated app installed and
  working on `dehati.ir`
