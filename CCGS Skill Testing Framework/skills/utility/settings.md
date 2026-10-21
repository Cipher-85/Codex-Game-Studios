# Skill Test Spec: $settings

## Skill Summary

Inspects candidate settings or previews assignments with the shared resolver.
Results include READY / INVALID / NOT ASSESSED and explicit staging/recovery
outcomes. Ordinary assignments remain read-only. A separate migration/rollback
branch requires concrete write approval. Review routing has an operational
consumer; other fields remain candidates. Inspection runs no workflow.
These cases specify native behavior, not records of executed skill invocations.

## Static Assertions

- [ ] Has Codex `name`/`description` frontmatter and ported metadata in the body.
- [ ] Has multiple phases and references the shared configuration contract/helper.
- [ ] Distinguishes read-only previews from partial consumer support; no delegation.
- [ ] Separates migration approval from package installation and inspection.
- [ ] Contains READY, INVALID and NOT ASSESSED; no guessed fallback on errors.

## Test Cases

### Case 1: Legacy project, no YAML

**Fixture:** Legacy review full, stage Pre-Production, custom testing prose.
**Input:** `$settings`
**Assertions:**
- [ ] Runs the resolver and reports legacy source paths.
- [ ] Leaves rigor unset rather than assigning standard/minimal.
- [ ] Reports custom prose as authoritative/unmigrated.
- [ ] Reads operational review mode/value/source through `review-mode`, labels
      the other fields as candidates, and creates no configuration files.

### Case 2: Inspect precedence from a nested directory

**Fixture:** Project rigor standard; local review full; working directory src/ui.
**Input:** `$settings modes.review_mode`
**Assertions:**
- [ ] Executes the bound project's helper with a root-independent path.
- [ ] Shows full from project.local.yaml as the supported review-routing value.
- [ ] Reports only `modes.review_mode` in `operational_keys`; other fields remain
      candidates. Does not claim a role agent or gate actually ran.

### Case 3: Preview rigor with an explicit override

**Fixture:** Project rigor standard and explicit docs.density terse.
**Input:** `$settings modes.rigor=full`
**Assertions:**
- [ ] Shows all candidate value/source changes returned by the helper.
- [ ] Density stays terse with its explicit provenance.
- [ ] Reports nothing written; neither YAML nor legacy mirrors change.
- [ ] A request to save reaches the assignment-write boundary without applying
      changes. Explicit rigor can supply review mode, but this preview is not saved.

### Case 4: Invalid input or local scope

**Fixtures:** Duplicate modes blocks; misspelled enum; wrong value shape;
locked local rigor; local file without base.
**Input:** `$settings` or `$settings --local modes.rigor=minimal`
**Assertions:**
- [ ] Reports INVALID with the helper's field/file diagnostic.
- [ ] Does not display fallback settings as a successful resolved configuration.
- [ ] Reads/previews enforce the same local whitelist.
- [ ] Does not repair or write files automatically.

### Case 5: Tooling unavailable and read-only closeout

**Fixture:** Python/helper unavailable, then repeat with valid tooling.
**Input:** `$settings modes.review_mode`
**Assertions:**
- [ ] Unavailable tooling yields NOT ASSESSED with the owed setup action.
- [ ] Valid tooling yields READY for inspection, not a claimed runtime test pass.
- [ ] Completes relevant read-only lookups before offering next actions.
- [ ] Ends with numbered options and one recommended action; no agents spawn.

### Case 6: Migration preview and approval boundary

**Fixture:** Legacy review/stage/engine fields, custom prose, no root YAML.
**Input:** `$settings migrate`, followed by approval of the exact shown changeset.
**Assertions:**
- [ ] Completes the read-only helper plan automatically before asking approval.
- [ ] Shows canonical root, mapping, unmapped prose, conflicts, full diff, plan ID,
      backup/receipt/lock paths, temporary-file pattern and exact apply command.
- [ ] Asks "May I write this to [all listed paths]?" with `a. yes` / `b. no`.
- [ ] A preview, package-install approval, or `migrate` alone causes no writes.
- [ ] Applies only the approved fresh plan. Stale inputs cause re-preview and
      renewed approval; conflicts are not repaired or overwritten.
- [ ] Reports STAGED and that subsequent review routing reads staged values;
      other fields remain candidates. Preserves legacy files and absent rigor,
      and never claims a native workflow or engine test passed.

### Case 7: Rollback, failure and repeated migration

**Fixtures:** Completed staging; second migration; later user edit; interrupted
transaction; write/restore failure; unavailable POSIX helper requirements.
**Input:** `$settings migrate` or `$settings rollback <transaction>`.
**Assertions:**
- [ ] A fresh second migration plan is noop and requests no redundant write.
- [ ] Rollback preview is read-only and needs separate approval of target and
      receipt changes before its fingerprinted command runs.
- [ ] Later edits, invalid receipts and stale rollback plans block restoration.
- [ ] Incomplete recovery reports RECOVERY REQUIRED, retained artifacts and all
      errors; it completes the read-only recovery preview before stopping.
- [ ] Does not simulate restored state, delete artifacts, force overwrite or
      execute workflows. Reports how restored inputs affect later review routing.
      Missing tooling yields NOT ASSESSED.

## Coverage Notes

Executable helper tests run through `validate_project_config.py` and
`validate_config_migration.py`. Installer fixtures cover package ownership and
preservation of root YAML, migration backups/receipts and the outside-block
ignore rule. Those checks do not establish
native skill discovery, approval UI behavior, actual gate spawns or engine execution.

## Phase 4B workflow and stage acceptance

Status: NOT RUN — native skill behavior requires a separate observed invocation.
The executable project-config/hook tests verify resolution, not this skill run.

- Run with no selected rigor/workflow: retain compatibility requirements and show
  the unset source; do not select minimal or standard implicitly.
- Run with explicit minimal, standard and full fixtures. Apply
  `.codex/docs/workflow-modes.md` before required-artifact checks, report source,
  and preserve existing optional documents. Standard numeric rules require
  Formulas; Detailed Design and Detailed Rules are aliases.
- For named systems, resolve the GDD filename stem per item. A future authoring
  stem is valid; a gate reports unmatched keys without silently applying them.
- When this skill plans or implements minimal work, use the brief's numbered MVP
  requirements. Do not demand optional registry/ADR/sprint artifacts, invent IDs,
  or waive concrete criteria and current story-type evidence requirements.
- When this skill reads/updates stage, use the shared reader and approved target.
  Test YAML overriding a stale legacy stage, unset stage, invalid configuration,
  and terminal Live. A declined write changes nothing; success needs readback.
- A no-input or zero-required-check review is NOT ASSESSED or explicitly NOT
  APPLICABLE, never evidence of a passing review or permission to advance.

## Phase 4C consumer acceptance

Status: NOT RUN — these cases need an observed native skill invocation.
The executable configuration tests validate resolution, not this workflow.

- Verify `technical` values/sources against YAML, legacy literals and actual pin
  files. Unmapped custom prose remains visible; wrong/missing pins and runners
  are not successful setup. Preserve custom routing and actual installed tools.
- For QA consumers, run every level with missing/failed required evidence and
  false strictness: closure/admission stays blocked. Check true strictness on
  an otherwise-advisory finding. Full adds affected-path regression evidence;
  an active coverage target needs an applicable measured report, not test counts.
- For team consumers, compare individual/small/studio and unconfigured rosters.
  Only explicitly optional participation changes. Required owners, conditional
  owners whose conditions hold, and surviving review gates remain present.
- Verify optional performance enforcement with measured data, missing data and
  estimates. Estimates never pass compliance. Off does not waive an acceptance
  criterion or erase an observed failure.
- Verify setup previews name every affected file, retain approval across the
  unchanged scope, reject stale previews, and re-read actual writes. No config
  reader installs, migrates, spawns, commits or changes root YAML by itself.
