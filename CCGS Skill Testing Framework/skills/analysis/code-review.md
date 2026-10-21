# Skill Test Spec: $code-review

## Skill Summary

`$code-review` performs an architectural code review of source files in `src/`,
checking coding standards from `AGENTS.md` (doc comments on public APIs,
dependency injection over singletons, data-driven values, testability). Findings
are advisory. No director gates are invoked. No code edits are made. Verdicts:
APPROVED, CONCERNS, or NEEDS CHANGES.

---

## Static Assertions (Structural)

Verified automatically by `$skill-test static` — no fixture needed.

- [ ] Has the Codex metadata contract: `name` and `description` in frontmatter; ported fields in `## Ported metadata`, or an explicit Codex-native support classification
- [ ] Has ≥2 phase headings
- [ ] Contains verdict keywords: APPROVED, CONCERNS, NEEDS CHANGES
- [ ] Does NOT require "May I write" language (read-only; findings are advisory output)
- [ ] Has a next-step handoff (what to do with findings)

---

## Director Gate Checks

None. Code review is a read-only advisory skill; no gates are invoked.

---

## Test Cases

### Case 1: Happy Path — Source file follows all coding standards

**Fixture:**
- `src/gameplay/health_component.gd` exists with:
  - All public methods have doc comments (`##` notation)
  - No singletons used; dependencies injected via constructor
  - No hardcoded values; all constants reference `assets/data/`
  - ADR reference in file header: `# ADR: docs/architecture/adr-004-health.md`
  - Referenced ADR has `Status: Accepted`

**Input:** `$code-review src/gameplay/health_component.gd`

**Expected behavior:**
1. Skill reads the source file
2. Skill checks all coding standards: doc comments, DI, data-driven, ADR status
3. All checks pass
4. Skill outputs findings summary with all checks PASS
5. Verdict is APPROVED

**Assertions:**
- [ ] Each coding standard check is listed in the output
- [ ] All checks show PASS when standards are met
- [ ] Skill reads referenced ADR to confirm its status
- [ ] Verdict is APPROVED
- [ ] No edits are made to any file

---

### Case 2: Needs Changes — Missing doc comment and singleton usage

**Fixture:**
- `src/ui/inventory_ui.gd` has:
  - 2 public methods without doc comments
  - Uses `GameManager.instance` (singleton pattern)
  - All other standards met

**Input:** `$code-review src/ui/inventory_ui.gd`

**Expected behavior:**
1. Skill reads the source file
2. Skill detects: 2 missing doc comments on public methods
3. Skill detects: singleton usage at specific lines (e.g., line 42, line 87)
4. Findings list the exact method names and line numbers
5. Verdict is NEEDS CHANGES

**Assertions:**
- [ ] Missing doc comments are listed with method names
- [ ] Singleton usage is flagged with file and line number
- [ ] Verdict is NEEDS CHANGES when BLOCKING-level standard violations exist
- [ ] Skill does not edit the file — findings are for the developer to act on
- [ ] Output suggests replacing singleton with dependency injection

---

### Case 3: Architecture Risk — ADR reference is Proposed, not Accepted

**Fixture:**
- `src/core/save_system.gd` has a header comment: `# ADR: docs/architecture/adr-010-save.md`
- `adr-010-save.md` exists but has `Status: Proposed`
- Code itself follows all other coding standards

**Input:** `$code-review src/core/save_system.gd`

**Expected behavior:**
1. Skill reads the source file
2. Skill reads referenced ADR — finds `Status: Proposed`
3. Skill flags this as ARCHITECTURE RISK (code is implementing an unaccepted ADR)
4. Other coding standard checks pass
5. Verdict is CONCERNS (risk flag is advisory, not a hard NEEDS CHANGES)

**Assertions:**
- [ ] Skill reads referenced ADR file to check its status
- [ ] ARCHITECTURE RISK is flagged when ADR status is Proposed
- [ ] Verdict is CONCERNS (not NEEDS CHANGES) for ADR risk — advisory severity
- [ ] Output recommends resolving the ADR before the code goes to production

---

### Case 4: Edge Case — No source files found at specified path

**Fixture:**
- User calls `$code-review src/networking/`
- `src/networking/` directory does not exist

**Input:** `$code-review src/networking/`

**Expected behavior:**
1. Skill attempts to read files in `src/networking/`
2. Directory or files not found
3. Skill outputs an error: "No source files found at `src/networking/`"
4. Skill suggests checking `src/` for valid directories
5. No verdict is emitted (nothing was reviewed)

**Assertions:**
- [ ] Skill does not crash when path does not exist
- [ ] Output names the attempted path in the error message
- [ ] Output suggests checking `src/` for valid file paths
- [ ] No verdict is emitted when there is nothing to review

---

### Case 5: Gate Compliance — No gate; LP may be consulted separately

**Fixture:**
- Source file follows most standards but has 1 CONCERNS-level finding (a magic number)
- `review-mode.txt` contains `full`

**Input:** `$code-review src/gameplay/loot_system.gd`

**Expected behavior:**
1. Skill reads and reviews the source file
2. No director gate is invoked (code review findings are advisory)
3. Skill presents findings with the CONCERNS verdict
4. Output notes: "Consider requesting a Lead Programmer review for architecture concerns"
5. Skill does not invoke any agent automatically

**Assertions:**
- [ ] No director gate is invoked in any review mode
- [ ] LP consultation is suggested (not mandated) in the output
- [ ] No code edits are made
- [ ] Verdict is CONCERNS for advisory-level findings

---

## Protocol Compliance

- [ ] Reads source file(s) and coding standards before reviewing
- [ ] Lists each coding standard check in findings output
- [ ] Does not edit any source files (read-only skill)
- [ ] No director gates are invoked
- [ ] Verdict is one of: APPROVED, CONCERNS, NEEDS CHANGES

---

## Coverage Notes

- Batch review of all files in a directory is not explicitly tested; behavior
  is assumed to apply the same checks file by file and aggregate the verdict.
- Test coverage checks (verifying corresponding test files exist) are a stretch
  goal not tested here; that is primarily the domain of `$test-evidence-review`.

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

## Phase 5A source-scope acceptance

Status: NOT RUN — requires an observed native skill invocation. Configuration
fixture results do not prove this workflow's behavior.

- Resolve the source scope before scans/writes and retain its provenance.
  Test Godot, Unity and Unreal layouts plus an existing custom script folder.
  Use actual paths; never create `src/` to satisfy an example.
- Test lowercase `assets/`, missing conventional roots, conflicting engine
  markers and invalid configuration. Unresolved dependent checks stay
  NOT ASSESSED; no empty scan, fresh-project inference or clean verdict follows.
- Keep source and content scope distinct. Inspect native scenes, local packages
  and plugins where applicable; show scan denominators and exclusions. A
  resolved directory alone supplies no scan, build, coverage or playtest proof.
- Preserve engine-native test locations, explicit target paths, custom layout,
  role ownership and existing write/engine approval gates. A mixed native/custom
  project must not silently omit a source location or follow an external link.
