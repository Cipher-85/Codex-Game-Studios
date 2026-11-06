---
name: settings
description: "Inspect CCGS settings, plan and apply explicitly approved assignments, or stage a legacy configuration migration. Use when diagnosing ignored settings or preparing YAML migration."
---

## Technical configuration

Before using engine, framework, platform or performance fields, read
`.codex/docs/technical-config.md` and run `project_config.py technical`. Use its
resolved values/provenance for typed fields; the technical-preferences reads
below still supply custom prose, policies and routing notes. Check conflicts
and field-specific readiness before affected work. Pin agreement is not an
engine run; runner availability needs actual metadata/help verification. Keep
estimates separate from measured evidence and preserve existing pins/runners.


## Workflow policy

When explaining connected settings, read `.codex/docs/workflow-modes.md` and
use `project_config.py workflow` for effective policy. This diagnostic skill
still reports invalid configuration and can show schema guidance; it does not
route production work or require a passing workflow to inspect an error.

# Settings

Inspect settings or prepare a separately approved migration. Review-mode
routing, workflow, density, story granularity, stage, QA, team and technical
consumers are operational within their shared contracts. Inspection and plans are read-only. Assignments and migration/rollback write
only the exact paths approved in Phase 3.

## Phase 1: Resolve the Request

Bind the canonical project root. Read `.codex/docs/config-resolution.md`, then
run the installed `.codex/lib/project_config.py` through Python 3. Use its absolute
path when outside the root. Do not rely on shell preprocessing or a previous
configuration result; read current settings for this invocation.

| Argument | Helper subcommand |
|----------|-------------------|
| none | `resolve` |
| `<key>` | `resolve --key <key>` |
| `<key>=<value>` | `migrate_project_config.py settings-plan --set <key>=<value>` |
| `--local <key>=<value>` | `migrate_project_config.py settings-plan --local --set <key>=<value>` |
| `--system <name>` | `resolve --system <name>` |

For assignments, `migrate` or `rollback <transaction>`, read
`.codex/docs/config-migration.md` and use `migrate_project_config.py` instead:
`migrate` runs `plan`; `rollback <transaction>` runs `rollback-plan <transaction>`.
These read-only phases run automatically through the complete preview. Bind the
same canonical root and quote each argument; do not accept an arbitrary plan file.

Pass each assignment as one safely quoted argument. On unknown keys, invalid
values/configuration, locked local fields or missing base, show the helper's
error and stop that request. Never replace an invalid result with guessed
defaults. For syntax help or supported keys, run `schema` and explain the relevant
fields. If the helper/Python is unavailable, report NOT ASSESSED and the required
setup; do not reconstruct precedence by hand.

## Phase 2: Show the Result

For inspection, show requested values and sources. With no key, group the defined
settings concisely and identify meaningful unset values. Always state
**The reported operational keys are supported; other settings are candidates**. Report the helper's
`operational_keys`. For an unmodified inspection that includes review mode, also
run `project_config.py review-mode` and show its validated value/source. Report
INVALID/NOT ASSESSED without guessed fallback if that read fails. Surface legacy
prose limits and local shadows. Reading configuration runs no director gate or
acceptance check. For QA/team/technical fields, run the matching shared reader
and report effective constraints, inactive coverage targets, pin/runner limits
and unresolved conflicts. Explicit rigor supplies all six linked knobs;
automation remains a candidate and grants no authority.

For an assignment, show the full settings plan: exact file diffs, plan ID,
backup/receipt paths, effective_changes and every changed value/source, including
rigor-derived changes. Keep unchanged explicit settings visible when
explaining why rigor does not move them. Say **Preview only — nothing written**.
Empty effective_changes can still accompany a file edit shadowed by a local
override. Explain both. A noop plan writes nothing and needs no approval.

## Phase 3: Assignment or Migration Approval and Staging

Skip this phase for ordinary inspections. For an assignment plan, obtain approval
for all paths and the exact plan before calling `settings-apply --expect-plan
<plan_id>` with the identical `--set` arguments and `--local` flag. Plan IDs prove
freshness, not approval. Decline means no writes. Changed input requires a new
plan and approval. The resolver remains read-only; no consumer is executed.

For assignment/migration/rollback, show the canonical root, full changeset/diffs, plan ID,
mapped fields/provenance, unmapped prose, conflicts, backup/receipt/lock paths
and temporary-file pattern. Explain **Operational keys affect subsequent consumers;
other fields are staged candidates**. `activation: preview-only` and `applied: false` on inspection or
migration results mean this command ran no consumer, not that all YAML is inert.
Migration preserves existing project YAML; assignments change only their approved
leaf values. Every legacy file remains unchanged; no rigor is inferred.
For a blocked plan, show diagnostics and stop mutations. A noop requires no write
approval or application. Do not overwrite conflicts, repair YAML or delete an
unfinished transaction to get past a blocker.

For a ready plan, ask **May I write this to [all listed paths]?** Include the
exact apply/rollback command and `a. yes` / `b. no`. Approval must cover the full
changeset, artifacts and root; carry it forward only while that plan stays fresh.
Package-install approval or the word `migrate` alone does not approve its writes.
After approval run the command for the previewed operation: `settings-apply`
with the same assignments/local scope and `--expect-plan <plan_id>`, migration
`apply --expect-plan <plan_id>`, or
`rollback <transaction> --expect-plan <rollback_plan_id>`. Re-preview after a
stale refusal and request approval for changed proposals. Local YAML creation is allowed only by the approved local assignment plan. Keep
legacy mirror edits, package installation and workflow execution outside this transaction.

Report the helper's exact result. `staged` means project-owned files were written and operational settings are
available to subsequent consumers;
`rolled_back` means restored; `failed_rolled_back` means staging failed and
original targets were restored. `recovery_required` must name retained artifacts
and all errors; do not claim restoration. Complete a read-only rollback preview
automatically when recovery is needed, then pause for its write approval.

## Phase 4: Close the Request

Return READY for valid inspections/previews, STAGED or ROLLED BACK for verified
transaction results, INVALID/BLOCKED for rejected input, RECOVERY REQUIRED for
incomplete recovery, or NOT ASSESSED for unavailable tooling. Name unresolved
configuration problems and distinguish staging failure from successful rollback.
End with numbered next actions and exactly one `(Recommended)` option. Complete
schema lookups and read-only explanation automatically before that final prompt.
No role-agent delegation is part of this skill.

## Ported metadata

Codex adaptation of upstream v1.2.0 settings inspection for the staged
configuration migration. Assignment writes use the approved transaction above; automation behavior remains deferred.

- `argument-hint: [key | key=value | --local key=value | --system name | migrate | rollback transaction]`
- `user-invocable: true`
- `allowed-tools: Read, Bash`

### Assignment readback

After STAGED, run `project_config.py resolve` and the affected consumer reader.
Report the saved path, effective value and provenance; a local shadow remains
visible. Saved automation preferences remain candidates and grant no execution
authority. The same `rollback-plan` / `rollback` path handles assignment receipts.
Block-list replacement, scalar-to-mapping replacement and unsupported YAML are
refused rather than rewritten; explain the required explicit edit.
