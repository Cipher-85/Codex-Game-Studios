# Configuration Staging Transaction

Phase 3 adds an explicit migration transaction, separate from package installation.
It stages project-owned configuration. The shared readers already consume valid
YAML without a migration receipt. `operational_keys` lists review/workflow, QA/team and technical consumers; staged values affect those subsequent
consumers. Other fields remain candidates, with legacy technical prose still
authoritative for unmigrated consumers. `activation: preview-only` and
`applied: false` mean this transaction executed no consumer, including after a
successful file write (`status: staged`, `staged: true`).

## Preview and approval

Python 3.11+ on macOS/Linux is required (standard library, including POSIX `fcntl`
locking). Use the bound project's installed helper. The default root comes from
the helper's location; `--root` precedes the subcommand when selecting a fixture
or explicit project. Commands accept no arbitrary plan file or output paths.

```bash
python3 .codex/lib/migrate_project_config.py plan
```

The read-only JSON preview includes:

- Canonical root, input SHA-256 fingerprints, presence and file modes, tool
  fingerprints, migration history and a deterministic `plan_id`.
- Legacy review/stage and supported literal technical mappings with sources; unmapped technical
  prose and explicit YAML/legacy conflicts. No rigor or engine version is guessed.
- Exact target contents and diffs, backup/receipt paths, the shared lock path,
  and the temporary-file pattern used for atomic replacements.

`ready` means changes are available for approval; `noop` means nothing needs
staging; `blocked` requires resolving the reported conflict/error. A preview
creates no directories, locks, YAML, receipts or backups. Existing unsupported
or malformed YAML, a local file without a base, ambiguous duplicate engine or
language lines, symlinks, special files, and invalid legacy values block staging.
Inputs are bounded to 128 KiB. Existing project YAML is preserved byte for byte,
including comments, BOM and line endings. It is never automatically merged.

Show the complete preview and ask **May I write this to [the listed paths]?**
Approval must cover the full changeset, transaction artifacts and root. Then
run the exact command with that preview's ID:

```bash
python3 .codex/lib/migrate_project_config.py apply --expect-plan <plan_id>
```

The fingerprint is a freshness check, not evidence of user approval. The agent
must obtain approval through the project collaboration protocol. Recompute and
seek approval again if inputs, modes, tools, history or root change. Never treat
a settings value, a prior migration, or package-install approval as migration
authority. A direct request for a preview does not approve its application.

## Scope and ownership

The helper can change only two root files:

1. Create `project.yaml` **only if absent**, with `schema_version: 1` and mapped
   legacy fields. Absent fields keep resolver compatibility defaults; no knobs,
   strictness flags, rigor tier, or new engine pin are invented. If YAML already
   exists, missing fields continue to use legacy fallback. Explicit mismatches
   between YAML and legacy fields are conflicts requiring a separate decision.
2. Append a root-only `/project.local.yaml` ignore rule when needed, outside the
   installer's managed block. Existing bytes and file mode are preserved, with
   CRLF used for the appended lines when present. A later negation or a rule
   inside the removable managed block does not substitute for this final rule.
   The package template at `.codex/docs/templates/project.local.yaml` remains visible.

The helper never writes `project.local.yaml`, legacy files, technical-preference
prose, engine pins, role/model settings, continuity assets or install ownership
state. It executes no workflow. Root YAML, the appended ignore rule and
all migration backups/receipts are project-owned. Package install/upgrade only
distributes the helper, tests and instructions; it never invokes the migration.
Uninstall preserves the project files, migration artifacts and the outside-block
ignore rule. Automatic settings assignment writes are still deferred.

## Failure recovery and rollback

Each approved transaction retains `.codex/backups/config-migration/<plan_id>/`.
`before-<index>` holds each changed pre-existing file's exact bytes at mode 0600;
the receipt records original file modes, original absence, target hashes, plan
and status. The transaction directory is created at mode 0700. All backups and
an `applying` receipt must exist before the first target write.

The helper holds an exclusive nonblocking lock at
`.codex/backups/config-migration/transaction.lock`. The empty lock file remains;
the OS releases its lock when the process exits. Another transaction fails
without changing targets. Same-directory temporary files are flushed and
atomically replaced. Ordinary write failures trigger restoration of original
bytes, modes and absence. Final states are verified. This is a recoverable
two-file transaction, not a multi-file atomic filesystem commit or a guarantee
against power loss. The lock coordinates these helpers; stop concurrent editors
or installer runs for the transaction. A malicious concurrent filesystem writer
is outside this helper's threat model.

- `staged`: both target states and the final receipt were written and verified.
- `failed_rolled_back`: staging failed, and original target states were verified.
- `recovery_required`: recovery or journal persistence failed. Keep all artifacts,
  report every error and inspect the transaction; never claim restoration.
- An interrupted process may leave an `applying` or `rolling_back` receipt.
  New staging is blocked until recovery. A missing/invalid receipt also blocks
  new staging and requires manual inspection; do not delete it to bypass a gate.

Preview recovery/rollback using the exact transaction path from the result:

```bash
python3 .codex/lib/migrate_project_config.py rollback-plan .codex/backups/config-migration/<plan_id>
```

This read-only preview lists target reversals, receipt changes and its own ID.
Show it and obtain approval for all listed writes before running:

```bash
python3 .codex/lib/migrate_project_config.py rollback .codex/backups/config-migration/<plan_id> --expect-plan <rollback_plan_id>
```

Rollback verifies the receipt fingerprint, root, bounded target paths, backups,
and current target content/modes. For a completed staging it requires the exact
staged state; for interrupted recovery it accepts only known before/after states.
It refuses later user edits, deletions or mode changes, and stale rollback IDs.
Backups/receipts remain after rollback. If rollback stops partway, preserve the
artifacts and preview recovery again. Never force overwrite a later user edit.

A fresh migration preview after staging is `noop` and produces no new transaction.
Reusing a pre-staging ID is stale; it is not a second write authorization. After
rollback, a fresh preview incorporates history and can propose another separately
approved transaction. Exit 0 means ready/noop/staged/rolled_back; exit 2 means
blocked/failed_rolled_back/recovery_required. None of these is workflow QA evidence.

## Verification

`bash .codex/audit.sh config-migration` runs temporary-fixture regressions for
preview isolation, preservation, conflicts, freshness, partial/interrupted writes,
backups, locks, malformed receipts and rollback refusal after edits. The full
audit includes them. The installer matrix verifies shipping/removal and project
artifact preservation. These are helper and packaging checks; native `$settings`
approval behavior, actual gate spawns and remaining consumer migrations need
separate observation. Review-mode staging tests also check that preserved legacy
values resolve identically before staging and after an approved rollback.
